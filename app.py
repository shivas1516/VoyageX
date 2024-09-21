from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, get_flashed_messages
from flask_login import login_user
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
import secrets

# Load environment variables from .env file
load_dotenv()

# Initialize Firebase
cred = credentials.Certificate(os.getenv('FIREBASE_CREDENTIALS'))
firebase_admin.initialize_app(cred)

# Initialize Flask app and CSRF protection
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
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
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        existing_user = User.query.filter_by(email=email).first()
        
        if existing_user:
            flash('Email already registered. Please log in.', 'warning')
            return redirect(url_for('login'))
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return render_template('register.html')
        
        new_user = User(name=name, email=email, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/google_login')
def google_login():
    # Generate a random state string
    state = secrets.token_urlsafe(16)
    session['oauth_state'] = state
    redirect_uri = url_for('google_auth', _external=True)
    return google.authorize_redirect(redirect_uri, state=state)

@app.route('/google_login/google/authorized')
def google_auth():
    if 'oauth_state' not in session or request.args.get('state') != session['oauth_state']:
        flash('Invalid OAuth state', 'error')
        return redirect(url_for('login'))
    
    try:
        token = google.authorize_access_token()
        user_info = google.get('userinfo').json()
        email = user_info['email']
        
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email, name=user_info.get('name'))
            db.session.add(user)
            db.session.commit()
        
        login_user(user)
        session.pop('oauth_state', None)
        
        flash('Logged in successfully with Google!', 'success')
        return redirect(url_for('dashboard'))
    except Exception as e:
        flash('An error occurred during Google login. Please try again.', 'error')
        return redirect(url_for('login'))
    
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
    app.run(debug=False)
