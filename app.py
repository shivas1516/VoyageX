from flask import Flask, render_template, request, redirect, url_for, session, flash
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
logging.basicConfig(filename='app.log', level=logging.DEBUG)  # Use DEBUG level for development

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

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            user = auth.get_user_by_email(email)
            # Simulate Firebase authentication (replace with actual Firebase password verification)
            # Here, you should check the password against a hashed version stored in Firebase
            # For simplicity, we are skipping that step
            token = jwt.encode({
                'sub': user.uid,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            }, JWT_SECRET, algorithm='HS256')

            session['jwt_token'] = token
            session['user'] = email
            logging.info(f"User {email} logged in successfully.")
            return redirect(url_for('dashboard'))
        except Exception as e:
            logging.error(f"Login failed for {email}: {str(e)}")
            flash('Invalid credentials or user not found.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        try:
            user = auth.create_user(
                email=email,
                password=hashed_password
            )
            logging.info(f"User {email} registered successfully.")
            return redirect(url_for('login'))
        except Exception as e:
            logging.error(f"Registration failed for {email}: {str(e)}")
            flash('Error creating user.', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')

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

@app.route('/google_login/google/authorized')
def google_login():
    if not google.authorized:
        return redirect(url_for('google.login'))
    
    resp = google.get('/plus/v1/people/me')  # Adjust the API endpoint if necessary
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
    app.run(debug=True)  # Enable debug mode for development
