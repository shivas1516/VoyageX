from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import login_user
import firebase_admin
from firebase_admin import credentials, auth
import logging
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from flask_wtf import CSRFProtect, FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email
from dotenv import load_dotenv
import os
from authlib.integrations.flask_client import OAuth
import google.generativeai as genai
from prompt_text import prompt
from flask_wtf.csrf import CSRFError
from authlib.integrations.base_client import OAuthError


# Load environment variables from .env file
load_dotenv()

# Initialize Firebase
cred = credentials.Certificate(os.getenv('FIREBASE_CREDENTIALS'))
firebase_admin.initialize_app(cred)

# Initialize Flask app
app = Flask(__name__)

# Load configuration from environment variables or use default values
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')  # Use a secure default if not set
app.config['WTF_CSRF_SECRET_KEY'] = os.getenv('WTF_CSRF_SECRET_KEY', 'default_csrf_secret_key')  # Same here

# CSRF protection setup
csrf = CSRFProtect(app)

# Secure cookie settings
app.config['SESSION_COOKIE_SECURE'] = True  # Ensure cookies are only sent over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to cookies
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Control how cookies are sent with cross-site requests


# Secret key for JWT encoding/decoding
JWT_SECRET = os.getenv('JWT_SECRET_KEY')

# Initialize OAuth
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
)

# Login Form class
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

# Register Form class
class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

# Utility functions
def generate_jwt_token(user_id):
    """Generate a JWT token for a given user_id."""
    return jwt.encode({
        'sub': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, JWT_SECRET, algorithm='HS256')

def validate_jwt_token(token):
    """Validate the JWT token and handle token-related errors."""
    try:
        jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        flash('Token expired. Please log in again.', 'warning')
        return False
    except jwt.InvalidTokenError:
        flash('Invalid token. Please log in again.', 'danger')
        return False
    return True

def user_exists(email):
    """Check if a user exists in Firebase by their email."""
    try:
        auth.get_user_by_email(email)
        return True
    except firebase_admin.auth.UserNotFoundError:
        return False

def log_and_flash_error(message, category='danger'):
    """Helper function to log errors and flash messages."""
    logging.error(message)
    flash(message, category)

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    messages = []  # Initialize messages
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        # Firebase Email/Password Registration
        try:
            user = auth.create_user(
                email=email,
                password=password,
                display_name=name,
            )
            messages.append('User created successfully!')
            flash('User created successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            messages.append(f'Error creating user: {e}')
            flash(f'Error creating user: {e}', 'danger')

    return render_template('register.html', form=form, messages=messages)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    messages = []  # Initialize messages
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Firebase Email/Password login
        try:
            user = auth.get_user_by_email(email)
            # (You need to verify the password here using a REST API call)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            messages.append(f'Error logging in: {e}')
            flash(f'Error logging in: {e}', 'danger')

    return render_template('dashboard.html', form=form, messages=messages)

import os
import secrets

@app.route('/google_login')
def google_login():
    try:
        # Use Authlib's authorize_redirect method
        return google.authorize_redirect(redirect_uri=url_for('google_login_callback', _external=True))
    except Exception as e:
        app.logger.error(f"Error in google_login: {str(e)}")
        flash('An error occurred during login. Please try again.', 'danger')
        return redirect(url_for('login'))

@app.route('/google_login/google/authorized')
def google_login_callback():
    try:
        # Let Authlib handle the token exchange and state verification
        token = google.authorize_access_token()
        
        # If we get here, state verification was successful
        app.logger.info("State verification successful")
        
        # Get user info
        resp = google.get('userinfo')
        user_info = resp.json()
        
        # Check for necessary keys
        if 'email' not in user_info or 'name' not in user_info:
            app.logger.warning("Missing email or name in user info")
            flash('Failed to retrieve necessary user information.', 'danger')
            return redirect(url_for('login'))

        # Check if user already exists in Firebase
        try:
            user = auth.get_user_by_email(user_info['email'])
            app.logger.info(f"Existing user logged in: {user_info['email']}")
            flash('Logged in with Google', 'success')
        except auth.UserNotFoundError:
            # Create a new user in Firebase with Google details
            user = auth.create_user(
                email=user_info['email'],
                display_name=user_info['name'],
            )
            app.logger.info(f"New user registered: {user_info['email']}")
            flash('Registered and logged in with Google', 'success')

        # Store user session info
        session['user'] = user_info
        
        return redirect(url_for('dashboard'))

    except OAuthError as e:
        app.logger.error(f"OAuth Error: {str(e)}")
        flash('Authentication failed. Please try again.', 'danger')
        return redirect(url_for('landing'))
    except auth.AuthError as e:
        app.logger.error(f"Firebase Auth Error: {str(e)}")
        flash('An error occurred during authentication. Please try again.', 'danger')
        return redirect(url_for('landing'))
    except Exception as e:
        app.logger.error(f"Unexpected error in google_login_callback: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'danger')
        return redirect(url_for('landing'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session or 'jwt_token' not in session:
        flash('You must be logged in to access this page.', 'warning')
        return redirect(url_for('login'))

    if not validate_jwt_token(session['jwt_token']):
        return redirect(url_for('login'))

    return render_template('dashboard.html')

@app.route('/generate_plan', methods=['POST'])
def generate_content():
    if 'user' not in session or 'jwt_token' not in session:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401

    data = request.json

    required_fields = ['fromLocation', 'startDate', 'endDate', 'startTime', 'returnTime', 
                       'groupSize', 'totalBudget', 'predefinedTheme', 'numDestinations', 
                       'travelingMethod']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400

    user_input = prompt.format(
        fromLocation=data['fromLocation'],
        startDate=data['startDate'],
        endDate=data['endDate'],
        startTime=data['startTime'],
        returnTime=data['returnTime'],
        groupSize=data['groupSize'],
        totalBudget=data['totalBudget'],
        predefinedTheme=data['predefinedTheme'],
        numDestinations=data['numDestinations'],
        travelingMethod=data['travelingMethod'],
        destinations=', '.join(data.get('destinations', []))
    )
    
    print("User input for model:", user_input)  # Log the input

    try:
        # Use the Gemini API to generate content
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(user_input)

        if response.text:
            return jsonify({'success': True, 'text': response.text})
        else:
            return jsonify({'success': False, 'message': 'Generated content is empty'}), 500
    
    except genai.types.BlockedPromptException as e:
        print(f"Blocked prompt error: {e}")
        return jsonify({'success': False, 'message': 'The prompt was blocked due to content safety concerns'}), 400
    except genai.types.GenerationException as e:
        print(f"Generation error: {e}")
        return jsonify({'success': False, 'message': 'Failed to generate content due to an API error'}), 500
    except Exception as e:
        print(f"Unexpected error generating content: {e}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred while generating content'}), 500

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('landing'))

# Error handler for CSRF errors
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    flash('CSRF token missing or incorrect.', 'danger')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
