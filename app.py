from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import firebase_admin
from firebase_admin import credentials, auth
import logging
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from flask_wtf import CSRFProtect, FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from dotenv import load_dotenv
import os
from authlib.integrations.flask_client import OAuth
import google.generativeai as genai
from prompt_text import prompt
from flask_wtf.csrf import CSRFError
from authlib.integrations.base_client import OAuthError
import requests

# Load environment variables
load_dotenv()

# Initialize Firebase
cred = credentials.Certificate(os.getenv('FIREBASE_CREDENTIALS'))
firebase_admin.initialize_app(cred)

# Initialize Flask app
app = Flask(__name__)

# Set secret keys
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
if not app.config['SECRET_KEY']:
    raise ValueError("No SECRET_KEY set for Flask application")

# CSRF protection
csrf = CSRFProtect(app)
app.config['WTF_CSRF_SECRET_KEY'] = os.getenv('WTF_CSRF_SECRET_KEY')
if not app.config['WTF_CSRF_SECRET_KEY']:
    raise ValueError("No WTF_CSRF_SECRET_KEY set for Flask application")

# Secure cookie settings
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# CSRF protection
csrf = CSRFProtect(app)

# JWT configuration
JWT_SECRET = os.getenv('JWT_SECRET_KEY')
JWT_EXPIRATION = timedelta(hours=1)

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize OAuth
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
)

# Initialize Gemini AI
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, uid, email, display_name):
        self.id = uid
        self.email = email
        self.display_name = display_name

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(), 
        Length(min=8, message='Password must be at least 8 characters long'),
        EqualTo('confirm_password', message='Passwords must match')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    try:
        user = auth.get_user(user_id)
        return User(user.uid, user.email, user.display_name)
    except:
        return None

# Utility functions
def generate_jwt_token(user_id):
    return jwt.encode({
        'sub': user_id,
        'exp': datetime.utcnow() + JWT_EXPIRATION
    }, JWT_SECRET, algorithm='HS256')

def validate_jwt_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        flash('Session expired. Please log in again.', 'warning')
        return None
    except jwt.InvalidTokenError:
        flash('Invalid session. Please log in again.', 'danger')
        return None

# Routes
@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            # Check if user already exists
            try:
                existing_user = auth.get_user_by_email(form.email.data)
                flash('Email already in use. Please use a different email or try logging in.', 'warning')
                return render_template('register.html', form=form)
            except auth.UserNotFoundError:
                # User doesn't exist, proceed with creation
                pass

            # Create user in Firebase
            user = auth.create_user(
                email=form.email.data,
                password=form.password.data,
                display_name=form.name.data,
            )
            
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))

        except auth.EmailAlreadyExistsError:
            flash('An account with this email already exists.', 'danger')
        except auth.WeakPasswordError:
            flash('Password is too weak. Please choose a stronger password.', 'danger')
        except auth.InvalidEmailError:
            flash('Invalid email address. Please check and try again.', 'danger')
        except Exception as e:
            app.logger.error(f'Error during registration: {str(e)}')
            flash('An unexpected error occurred. Please try again later.', 'danger')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            # Authenticate with Firebase
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={os.getenv('FIREBASE_API_KEY')}"
            payload = {
                "email": form.email.data,
                "password": form.password.data,
                "returnSecureToken": True
            }
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                # Successfully authenticated
                auth_data = response.json()
                user = auth.get_user_by_email(form.email.data)
                user_obj = User(user.uid, user.email, user.display_name)
                login_user(user_obj)
                
                flash('Logged in successfully!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page or url_for('dashboard'))
            else:
                error_data = response.json()
                error_message = error_data.get('error', {}).get('message', 'Unknown error')
                
                if error_message == 'EMAIL_NOT_FOUND':
                    flash('No account found with this email. Please check your email or register.', 'danger')
                elif error_message == 'INVALID_PASSWORD':
                    flash('Incorrect password. Please try again.', 'danger')
                elif error_message == 'USER_DISABLED':
                    flash('This account has been disabled. Please contact support.', 'danger')
                else:
                    flash('Login failed. Please check your credentials and try again.', 'danger')
                
        except requests.RequestException:
            flash('Unable to connect to the authentication server. Please try again later.', 'danger')
        except Exception as e:
            app.logger.error(f'Error during login: {str(e)}')
            flash('An unexpected error occurred. Please try again later.', 'danger')

    return render_template('login.html', form=form)


@app.route('/google_login')
def google_login():
    return google.authorize_redirect(redirect_uri=url_for('google_login_callback', _external=True))

@app.route('/google_login/google/authorized')
def google_login_callback():
    try:
        token = google.authorize_access_token()
        user_info = google.get('userinfo').json()
        email = user_info.get('email')
        name = user_info.get('name')

        if not email or not name:
            raise ValueError("Missing email or name in user info")

        try:
            user = auth.get_user_by_email(email)
        except auth.UserNotFoundError:
            user = auth.create_user(email=email, display_name=name)

        user_obj = User(user.uid, user.email, user.display_name)
        login_user(user_obj)
        flash('Logged in with Google successfully!', 'success')
        return redirect(url_for('dashboard'))

    except OAuthError as e:
        flash(f'OAuth Error: {str(e)}', 'danger')
    except Exception as e:
        flash(f'An unexpected error occurred: {str(e)}', 'danger')

    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/generate_plan', methods=['POST'])
@login_required
def generate_content():
    data = request.json
    required_fields = ['fromLocation', 'startDate', 'endDate', 'startTime', 'returnTime', 
                       'groupSize', 'totalBudget', 'predefinedTheme', 'numDestinations', 
                       'travelingMethod']
    
    if not all(field in data for field in required_fields):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    user_input = prompt.format(**data, destinations=', '.join(data.get('destinations', [])))
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(user_input)

        if response.text:
            return jsonify({'success': True, 'text': response.text})
        else:
            return jsonify({'success': False, 'message': 'Generated content is empty'}), 500
    
    except genai.types.BlockedPromptException as e:
        return jsonify({'success': False, 'message': 'The prompt was blocked due to content safety concerns'}), 400
    except genai.types.GenerationException as e:
        return jsonify({'success': False, 'message': 'Failed to generate content due to an API error'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('landing'))

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    flash('CSRF token missing or incorrect.', 'danger')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)