from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, FloatField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange, ValidationError
import sqlalchemy as sa
from app import db
from app.models import User
from flask_login import current_user
# Register, Login, edit User info, logging saving amount for day or any moment
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    income = FloatField('Monthly Income', validators=[DataRequired(), NumberRange(min=0)]) 
    goal = FloatField('Savings Goal', validators=[DataRequired(), NumberRange(min=0)])
    savings = FloatField('Initial Savings', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Submit')
    
    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(User.username == username.data))
        if user is not None: # Scalar gets 1 query only, we are essentially checking if a username matches one in the database already so no duplicates. username.data refers to what the user entered thanks to self parameter 
            raise ValidationError('Please use a different username.') #means if user exist, none means no user exist, not is opisitie
         
    def validate_email(self, email): # These parameters are used within the class, not brought from outside 
        user = db.session.scalar(sa.select(User).where(User.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address')
class ExpenseForm(FlaskForm):
    # Well add both forms to the dashboard underneath the chart, both forms can be logged multiple times 
    # Index is our dashboard, we have to add the chart, pie, expense log, saving log there
    utilities = FloatField('Ulitities', validators=[DataRequired(), NumberRange(min=0)])
    food = FloatField('Food Cost', validators=[DataRequired(), NumberRange(min=0)])
    Miscellaneous = FloatField('Miscellaneous', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Log Expense')
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')
class EditProfileForm(FlaskForm):
    income = FloatField('New Monthly Income', validators=[DataRequired(), NumberRange(min=0)])
    goal = FloatField('New Savings Goal', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Update Money Info')
class SavingsLogForm(FlaskForm):
    amount = FloatField('Amount Saved', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Log Savings')