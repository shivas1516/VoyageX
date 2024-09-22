from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TimeField, IntegerField, SelectField, FieldList, FormField
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_login import UserMixin


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

class DestinationForm(FlaskForm):
    destination = StringField('Destination', validators=[DataRequired()])
    hotel = StringField('Preferred Hotel Name', validators=[DataRequired()])
    travel_preference = SelectField('Travel Preference', choices=[('', 'Select travel preference'), ('air', 'Air'), ('train', 'Train'), ('bus', 'Bus'), ('car', 'Car')])
    number_of_days = IntegerField('Number of Stay Days', validators=[DataRequired()])

class TravelForm(FlaskForm):
    from_location = StringField('From Location', validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    predefined_theme = SelectField('Select a Theme',choices=[('', 'Select theme'), ('family', 'Family'), ('honeymoon', 'Honeymoon'), 
            ('office_trip', 'Office Trip'), ('friends_trip', 'Friends Trip'), ('adventure', 'Adventure'), ('relaxation', 'Relaxation'), 
            ('cultural', 'Cultural'), ('nature', 'Nature'), ('beach', 'Beach'), ('historical', 'Historical'), ('wildlife', 'Wildlife'), 
            ('food_wine', 'Food & Wine'), ('luxury', 'Luxury'), ('romantic_getaway', 'Romantic Getaway'), ('solo_travel', 'Solo Travel')])
    start_time = TimeField('Starting Time', validators=[DataRequired()])
    return_time = TimeField('Returning Time', validators=[DataRequired()])
    group_size = IntegerField('Group Size', validators=[DataRequired()])
    total_budget = IntegerField('Total Budget (INR)', validators=[DataRequired()])
    num_destinations = IntegerField('Number of Destinations', validators=[DataRequired()])
    traveling_method = SelectField('Traveling Method', choices=[('', 'Select traveling method'), ('air', 'Air'), ('train', 'Train'), ('bus', 'Bus'), ('car', 'Car'), ('mix', 'Mix')])
    destinations = FieldList(FormField(DestinationForm), min_entries=1)
