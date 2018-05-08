
from flask_wtf import FlaskForm, Form
from wtforms import StringField, RadioField, PasswordField, BooleanField, SelectField, SubmitField, HiddenField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, Regexp
from datetime import datetime

from models import User
from address_validation import AddressValidator

class LoginForm(FlaskForm):
  """ Login Form  """
  username = StringField('Username', validators=[DataRequired()])
  password = PasswordField('Password', validators=[DataRequired()])
  remember_me = BooleanField('Remember Me')
  submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
  """ Registration Form  """
  months = [('01', '01'),('02', '02'),('03', '03'),('04', '04'),('05', '05'),('06', '06'),('07', '07'),('08', '08'),('09', '09'),('10', '10'),('11', '11'),('12', '12')]
  years = [('2018','2018'),('2019','2019'),('2020','2020'),('2021','2021'),('2022','2022'),('2023','2023'),('2024','2024'),('2025','2025'),('2026','2026')]

  role = RadioField('User Type', choices=[('user','user role'),('driver','driver role')],default='user')
  username = StringField('Username', validators=[DataRequired()])
  email = StringField('Email', validators=[DataRequired(), Email()])
  password = PasswordField('Password', validators=[DataRequired()])
  password2 = PasswordField(
      'Repeat Password', validators=[DataRequired(), EqualTo('password')])
  # Credit Card Information
  card_number = StringField('Credit Card Number', validators=[DataRequired(),
    Length(min=16,max=16,message='Credit Card number must be 16-digits'),
    Regexp(regex='[0-9]',message="Must use digits 0-9")])
  exp_month = SelectField('Experation Month', choices=months, validators=[DataRequired()], default='05')
  exp_year = SelectField('Experation Year', choices=years, validators=[DataRequired()])
  cvc = StringField('CVC', validators=[DataRequired(),
    Regexp(regex='[0-9]',message="Must use digits 0-9")])
  zipcode = StringField('Zipcode', validators=[DataRequired(),
    Length(min=5,max=5,message='Invalid zipcode'),
    Regexp(regex='[0-9]',message="Must use digits 0-9")])
  submit = SubmitField('Register')

  def validate_username(self, username):
    user = User.query.filter_by(username=username.data).first()
    if user is not None:
      raise ValidationError('Please use a different username.')

  def validate_email(self, email):
    user = User.query.filter_by(email=email.data).first()
    if user is not None:
      raise ValidationError('Please use a different email address.')
    if email.data.split('@')[0][-1] == '.':
      raise ValidationError('Invalid Email. . befor @ detected')

  def validate_exp_month(self, exp_month):
    now = datetime.now()
    if now.month >= int(exp_month.data):
      raise ValidationError('Expired Expiration Detected')

  def validate_exp_year(self, exp_year):
    now = datetime.now()
    if now.year >= int(exp_year.data):
      raise ValidationError('Expired Expiration Detected')


class AcceptRideRequestForm(FlaskForm):
  """ Accepts Ride Request Fomrs 
      instantiated from driver """
  request_id = HiddenField('request_id')
  submit = SubmitField('Accept Ride Request')

class RideRequestForm(FlaskForm):
  """ Ride Request Form 
      instantiated from user """
  # start location of request (defalut start location home)
  startLocation = StringField('Start Location', validators=[DataRequired()])
  # end location of request (default end location airports)
  choices = [('San Jose Airport', 'San Jose Airport'),('San Francisco Airport', 'San Francisco Airport'),('Oakland Airport', 'Oakland Airport')]
  endLocation = SelectField('End Location', choices=choices, validators=[DataRequired()])
  # submit button
  submit = SubmitField('Request Ride')

  def validate(self):
    """ handles all address validation """
    rv = FlaskForm.validate(self)
    if not rv:
      return False

    # Validate Addresses
    origin_validator = AddressValidator()
    # Check if not valid origin
    if not origin_validator.is_valid_address(self.startLocation.data):
      self.startLocation.errors.append('Origin: Invalid Location')
      return False

    dest_validator = AddressValidator()
    # check if not valid destination
    if not dest_validator.is_valid_address(self.endLocation.data):
      self.endLocation.errors.append('Destination: Invalid Location')
      return False

    # check if origin and destination are the same
    if origin_validator.address == dest_validator.address:
      self.startLocation.errors.append('Origin cannot match destination')
      self.endLocation.errors.append('Destination cannot match origin')
      return False

    # check if there are logged in drivers
    users = User.query.all()
    drivers = []
    for u in users:    
      if u.has_roles('driver') and u.is_logged_in():
        drivers.append(u)
    if len(drivers) == 0:
      self.startLocation.errors.append('There are no available drivers at this time')
      self.endLocation.errors.append('There are no available drivers at this time')
      return False

    # If address validation passes, check for available drivers
    self.startLocation = origin_validator.address
    self.endLocation = dest_validator.address

    # all vaidations passed
    return True

    
