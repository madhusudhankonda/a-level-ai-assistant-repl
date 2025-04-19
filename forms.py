from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, SelectMultipleField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional

class LoginForm(FlaskForm):
    """Form for user login"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')

class SignupForm(FlaskForm):
    """Form for user registration"""
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=64, message="Username must be between 3 and 64 characters")
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message="Please enter a valid email address")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message="Password must be at least 8 characters long")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message="Passwords must match")
    ])
    terms_consent = BooleanField('I have read and agree to the <a href="/terms" target="_blank">Terms and Conditions</a>', validators=[
        DataRequired(message="You must agree to the Terms and Conditions to register")
    ])
    privacy_consent = BooleanField('I have read and agree to the <a href="/privacy" target="_blank">Privacy Policy</a>', validators=[
        DataRequired(message="You must agree to the Privacy Policy to register")
    ])
    age_consent = BooleanField('I confirm that I am at least 16 years old', validators=[
        DataRequired(message="You must be at least 16 years old to use this service")
    ])
    marketing_consent = BooleanField('I agree to receive updates about new features and educational content (optional)')

class ProfileEditForm(FlaskForm):
    """Form for editing user profile"""
    first_name = StringField('First Name', validators=[Optional(), Length(max=50)])
    last_name = StringField('Last Name', validators=[Optional(), Length(max=50)])
    school_name = StringField('School Name', validators=[Optional(), Length(max=100)])
    grade_year = SelectField('Year/Grade', choices=[
        ('', 'Select Year/Grade'),
        ('Year 12', 'Year 12 (AS Level)'),
        ('Year 13', 'Year 13 (A Level)'),
        ('Year 11', 'Year 11 (GCSE)'),
        ('University', 'University'),
        ('Other', 'Other')
    ], validators=[Optional()])
    preferred_subjects = SelectMultipleField('Preferred Subjects', choices=[
        ('Mathematics', 'Mathematics'),
        ('Physics', 'Physics'),
        ('Chemistry', 'Chemistry'),
        ('Biology', 'Biology')
    ], validators=[Optional()])