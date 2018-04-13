
from flask_wtf import FlaskForm, Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

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
  username = StringField('Username', validators=[DataRequired()])
  email = StringField('Email', validators=[DataRequired(), Email()])
  password = PasswordField('Password', validators=[DataRequired()])
  password2 = PasswordField(
      'Repeat Password', validators=[DataRequired(), EqualTo('password')])
  submit = SubmitField('Register')

  def validate_username(self, username):
    user = User.query.filter_by(username=username.data).first()
    if user is not None:
      raise ValidationError('Please use a different username.')

  def validate_email(self, email):
    user = User.query.filter_by(email=email.data).first()
    if user is not None:
      raise ValidationError('Please use a different email address.')

class CreditCardForm(FlaskForm):
  """ Credit Card Form """
  card = StringField('Card Number', validators=[DataRequired()])
  exp = StringField('Expiration Date', validators=[DataRequired()])
  cvc = StringField('CVC', validators=[DataRequired()])
  zipcode = StringField('Zipcode', validators=[DataRequired()])

  def validate_card(self, card, exp, csv, zipcode):
    return false

class RideRequestForm(FlaskForm):
  """ Address Form """
  startLocation = StringField('Start Location', validators=[DataRequired()])
  endLocation = StringField('End Location', validators=[DataRequired()])
  submit = SubmitField('Request Ride')

  def validate(self):
    """ handles all address validation """
    rv = FlaskForm.validate(self)
    if not rv:
      return False

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

    # if self.startLocation.data == self.endLocation.data:
    #   self.startLocation.errors.append('Origin cannot match destination')
    #   self.endLocation.error.append('Destination cannot match origin')
    #   return False
    
    # Passed validation
    self.startLocation = origin_validator.address
    self.endLocation = dest_validator.address
    return True

    
