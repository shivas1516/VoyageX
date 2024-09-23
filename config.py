import firebase_admin
from firebase_admin import credentials
from flask_wtf import CSRFProtect
import os
from flask import Flask
from datetime import timedelta
from authlib.integrations.flask_client import OAuth

# Initialize Firebase
cred = credentials.Certificate(os.getenv('FIREBASE_CREDENTIALS'))

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

# Initialize Firebase
firebase_admin.initialize_app(cred)