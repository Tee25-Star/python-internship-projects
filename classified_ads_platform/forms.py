from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, SelectField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, ValidationError
from flask import current_app


class RegistrationForm(FlaskForm):
    """Form for user registration"""
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        from models import User
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_email(self, email):
        from models import User
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')


class LoginForm(FlaskForm):
    """Form for user login"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class AdForm(FlaskForm):
    """Form for creating/editing ads"""
    title = StringField('Title', validators=[DataRequired(), Length(min=5, max=200)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10)])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    location = StringField('Location', validators=[DataRequired(), Length(max=200)])
    contact_info = StringField('Contact Information', validators=[DataRequired(), Length(max=200)])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Post Ad')


class SearchForm(FlaskForm):
    """Form for searching ads"""
    query = StringField('Search', validators=[Length(max=200)])
    category_id = SelectField('Category', coerce=int, default=0)
    min_price = FloatField('Min Price', validators=[NumberRange(min=0)])
    max_price = FloatField('Max Price', validators=[NumberRange(min=0)])
    location = StringField('Location', validators=[Length(max=200)])
    submit = SubmitField('Search')
