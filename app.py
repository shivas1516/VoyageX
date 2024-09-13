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

# Initialize logging
#logging.basicConfig(filename='app.log', level=logging.DEBUG)  # Use DEBUG level for development

# Secret key for JWT encoding/decoding
JWT_SECRET = os.getenv('JWT_SECRET_KEY')

# Initialize OAuth
oauth = OAuth(app)
google_bp = make_google_blueprint(
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    redirect_to='google_login'
)
app.register_blueprint(google_bp, url_prefix='/google_login')


# Define the Gemini API URL and key (assuming it's in your environment variables)
GEMINI_API_URL = os.getenv('GEMINI_API_URL')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Configure the Google AI API
genai.configure(api_key='GEMINI_API_KEY')


@app.route('/')
def landing():
    return render_template('landing.html')

# Login Form class
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])


# Register Form class
class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # Create an instance of LoginForm
    
    if form.validate_on_submit():  # Handle form submission
        email = form.email.data  # Get the email from the form
        password = form.password.data  # Get the password from the form

        try:
            user = auth.get_user_by_email(email)

            try:
                # Firebase Authentication password verification
                user_record = auth.verify_password(email, password)
                token = jwt.encode({
                    'sub': user.uid,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
                }, JWT_SECRET, algorithm='HS256')

                session['jwt_token'] = token
                session['user'] = email
                logging.info(f"User {email} logged in successfully.")
                flash('Logged in successfully!', 'success')
                return redirect(url_for('dashboard'))

            except auth.AuthError:
                logging.error(f"Incorrect password for {email}")
                flash('Invalid password. Please try again.', 'danger')
                return redirect(url_for('login'))

        except auth.UserNotFoundError:
            logging.error(f"Login failed: User with email {email} not found.")
            flash('Email not found. Please check your email or sign up.', 'danger')
            return redirect(url_for('login'))

        except Exception as e:
            logging.error(f"Login failed for {email}: {str(e)}")
            flash('An error occurred during login. Please try again later.', 'danger')
            return redirect(url_for('login'))

    # Get flash messages and ensure they are defined
    messages = get_flashed_messages(with_categories=True) or []

    # Render the login template with the form and flash messages
    return render_template('login.html', form=form, messages=messages)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()  # Create an instance of RegisterForm

    if form.validate_on_submit(): 
        name = form.name.data  
        email = form.email.data  
        password = form.password.data 
        hashed_password = generate_password_hash(password)

        try:
            # Create user with name and email
            user = auth.create_user(
                email=email,
                password=hashed_password,
                display_name=name
            )
            logging.info(f"User {email} registered successfully.")
            flash('Registration successful!', 'success')
            return  render_template('dashboard.html')
        except Exception as e:
            logging.error(f"Registration failed for {email}: {str(e)}")
            flash('Error creating user.', 'danger')
            return redirect(url_for('register'))

    # Retrieve flash messages
    messages = get_flashed_messages(with_categories=True) or []

    # Render the register template with the form and flash messages
    return render_template('register.html', form=form, messages=messages)


@app.route('/dashboard')
def dashboard():
    if 'user' not in session or 'jwt_token' not in session:
        flash('You must be logged in to access this page.', 'warning')
        return redirect(url_for('login'))
    
    try:
        jwt.decode(session['jwt_token'], JWT_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        flash('Token expired. Please log in again.', 'warning')
        return redirect(url_for('login'))
    except jwt.InvalidTokenError:
        flash('Invalid token. Please log in again.', 'danger')
        return redirect(url_for('login'))

    return render_template('dashboard.html')


@app.route('/generate_plan', methods=['POST'])
def generate_plan():
    try:
        # Get JSON data from the request
        data = request.json
        formatted_prompt = prompt.format(user_data=json.dumps(data, indent=2))
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(formatted_prompt)
        generated_itinerary = response.text
        response_data = {
            "itinerary": generated_itinerary
        }

        # Return the response as JSON
        return jsonify(response_data), 200

    except Exception as e:
        # Handle any errors
        error_response = {
            "error": str(e)
        }
        return jsonify(error_response), 500


@app.route('/google_login/google/authorized')
def google_login():
    if not google.authorized:
        return redirect(url_for('google.login'))
    
    resp = google.get('/plus/v1/people/me')
    assert resp.ok, resp.text
    email = resp.json()['emails'][0]['value']
    session['user'] = email
    logging.info(f"User {email} logged in with Google OAuth.")
    return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('jwt_token', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('landing'))


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    flash('CSRF token missing or incorrect.', 'danger')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
