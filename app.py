from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, get_flashed_messages
import firebase_admin
from firebase_admin import credentials, auth
import logging
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError
from dotenv import load_dotenv
import os
from authlib.integrations.flask_client import OAuth
from flask_dance.contrib.google import make_google_blueprint, google
import requests
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email
import google.generativeai as genai
import json
from prompt_text import prompt

# Load environment variables from .env file
load_dotenv()

# Initialize Firebase
cred = credentials.Certificate(os.getenv('FIREBASE_CREDENTIALS'))
firebase_admin.initialize_app(cred)

# Initialize Flask app and CSRF protection
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')  # Load secret key from environment
csrf = CSRFProtect(app)

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        if not user_exists(email):
            log_and_flash_error(f"Login failed: User with email {email} not found.")
            return redirect(url_for('login'))

        try:
            user = auth.get_user_by_email(email)
            if not check_password_hash(user.password, password):
                raise auth.InvalidPasswordError

            session['jwt_token'] = token
            session['user'] = email

            logging.info(f"User {email} logged in successfully.")
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))

        except auth.InvalidPasswordError:
            log_and_flash_error(f"Invalid password for {email}")
            return redirect(url_for('login'))
        except auth.AuthError as auth_error:
            log_and_flash_error(f"Authentication error for {email}: {str(auth_error)}")
            return redirect(url_for('login'))
        except Exception as e:
            log_and_flash_error(f"Unexpected error during login for {email}: {str(e)}")
            return redirect(url_for('login'))

    messages = get_flashed_messages(with_categories=True) or []
    return render_template('login.html', form=form, messages=messages)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        if user_exists(email):
            flash('Email is already registered. Please log in.', 'warning')
            logging.warning(f"Attempted registration with existing email: {email}")
            return redirect(url_for('login'))

        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return redirect(url_for('register'))

        try:
            hashed_password = generate_password_hash(password)
            user = auth.create_user(
                email=email,
                password=hashed_password,
                display_name=name
            )
            
            logging.info(f"User {email} registered successfully.")
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))

        except auth.InvalidEmailError:
            log_and_flash_error(f"Invalid email address during registration: {email}")
            return redirect(url_for('register'))
        except auth.WeakPasswordError:
            log_and_flash_error(f"Weak password attempt for {email}")
            return redirect(url_for('register'))
        except auth.AuthError as auth_error:
            log_and_flash_error(f"Authentication error during registration for {email}: {str(auth_error)}")
            return redirect(url_for('register'))
        except Exception as e:
            log_and_flash_error(f"Unexpected error during registration for {email}: {str(e)}")
            return redirect(url_for('register'))

    messages = get_flashed_messages(with_categories=True) or []
    return render_template('register.html', form=form, messages=messages)

# Update the google_login route
@app.route('/google_login')
def google_login():
    redirect_uri = url_for('google_auth', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/google_login/google/authorized')
def google_auth():
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    email = user_info['email']
    
    session['user'] = email
    logging.info(f"User {email} logged in with Google OAuth.")
    
    # Generate JWT for authenticated users
    user_record = auth.get_user_by_email(email) if user_exists(email) else auth.create_user(email=email)
    token = generate_jwt_token(user_record.uid)
    session['jwt_token'] = token
    
    return redirect(url_for('dashboard'))

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
    session.pop('user', None)
    session.pop('jwt_token', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('landing'))

# Error handler for CSRF errors
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    flash('CSRF token missing or incorrect.', 'danger')
    return redirect(url_for('login'))