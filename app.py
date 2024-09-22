from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import  login_user, logout_user, login_required, current_user
from firebase_admin import auth
from dotenv import load_dotenv
import google.generativeai as genai
from prompt_text import prompt
from flask_wtf.csrf import CSRFError
from authlib.integrations.base_client import OAuthError
import requests
import logging
import traceback
import os
from forms import User, RegisterForm, LoginForm, TravelForm
from config import app, google, login_manager

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    try:
        user = auth.get_user(user_id)
        return User(user.uid, user.email, user.display_name)
    except:
        return None

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            # Check if user already exists
            try:
                existing_user = auth.get_user_by_email(form.email.data)
                flash('Email already in use. Please use a different email or try logging in.', 'warning')
                return render_template('register.html', form=form)
            except auth.UserNotFoundError:
                pass

            # Create user in Firebase
            user = auth.create_user(
                email=form.email.data,
                password=form.password.data,
                display_name=form.name.data,
            )
            return redirect(url_for('dashboard'))

        except auth.InvalidEmailError:
            flash('Invalid email address. Please check and try again.', 'danger')
        except Exception as e:
            app.logger.error(f'Error during registration: {str(e)}')
            flash('An unexpected error occurred. Please try again later.', 'danger')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
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

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = TravelForm()
    if form.validate_on_submit():
        # Gather data from the form
        data = {
            'fromLocation': form.from_location.data,
            'startDate': form.start_date.data,
            'endDate': form.end_date.data,
            'predefinedTheme': form.predefined_theme.data,
            'startTime': form.start_time.data,
            'returnTime': form.return_time.data,
            'groupSize': form.group_size.data,
            'totalBudget': form.total_budget.data,
            'numDestinations': form.num_destinations.data,
            'travelingMethod': form.traveling_method.data,
        }

        # Collect destination data
        destinations = []
        for i in range(1, form.num_destinations.data + 1):
            destination_field = getattr(form, f'destination{i}', None)
            if destination_field:
                destinations.append(destination_field.data)

        data['destinations'] = destinations
        destinations_str = ', '.join(destinations)

        # Logging for debugging
        logging.debug(f"From Location: {data['fromLocation']}, Start Date: {data['startDate']}, End Date: {data['endDate']}")
        logging.debug(f"Destinations: {destinations_str}")

        # User input for the model
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
            destinations=destinations_str
        )

        logging.debug(f"User Input for Model: {user_input}")

        try:
            model = genai.GenerativeModel("gemini-1.5-pro")
            response = model.generate_content(user_input)

            logging.debug(f"Model Response: {response.text}")

            # Return the generated plan if successful
            if response.text:
                return jsonify({
                    'success': True,
                    'plan': {
                        'raw_text': response.text
                    }
                })
            else:
                return jsonify({'success': False, 'message': 'Generated content is empty'}), 500

        except genai.types.BlockedPromptException as e:
            logging.error(f"Blocked Prompt Exception: {e}")
            return jsonify({'success': False, 'message': 'The prompt was blocked due to content safety concerns'}), 400
        except genai.types.GenerationException as e:
            logging.error(f"Generation Exception: {e}")
            return jsonify({'success': False, 'message': 'Failed to generate content due to an API error'}), 500
        except Exception as e:
            logging.error(f"Unexpected Error: {str(e)}")
            logging.error(traceback.format_exc())
            return jsonify({'success': False, 'message': f'An unexpected error occurred: {str(e)}'}), 500
        
    return render_template('dashboard.html', form=form)

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