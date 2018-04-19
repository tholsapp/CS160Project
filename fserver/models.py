
from passlib.hash import pbkdf2_sha256

from flask_security import UserMixin, RoleMixin
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Binary, Boolean, DateTime, Column, Integer, \
                       String, ForeignKey, func
from datetime import datetime
from fserver.database import db


class RideRequest(db.Model):
  """ Ride Request """
  __tablename__ = 'ride_request'
  id = db.Column(db.Integer(), primary_key=True, unique=True)
  origin = db.Column(db.String(255))
  destination = db.Column(db.String(255))
  time_of_request = db.Column(db.DateTime())
  time_of_pickup = db.Column(db.DateTime())
  time_of_dropoff = db.Column(db.DateTime())
  group_ride = db.Column(db.Boolean(), default=False)

  def is_active_ride(self):
    if time_of_request == time_of_dropoff:
      return False
    return True

  def has_been_picked_up(self):
    if time_of_request == time_of_pickup:
      return False
    return True


class Role(db.Model, RoleMixin):
  """ Role Model """
  __tablename__ = 'role'
  id = db.Column(Integer(), primary_key=True, unique=True)
  name = db.Column(db.String(80), unique=True)
  description = db.Column(db.String(255))


class User(db.Model, UserMixin):
  """ User model """
  __tablename__ = 'user'
  id = db.Column(db.Integer, primary_key=True, unique=True)
  email = db.Column(db.String(255), unique=True)
  username = db.Column(db.String(64), unique=True)
  password = db.Column(db.String(255))
  last_login_at = db.Column(db.DateTime())
  current_login_at = db.Column(db.DateTime())
  last_login_ip = db.Column(db.String(100))
  current_login_ip = db.Column(db.String(100))
  login_count = db.Column(db.Integer())
  confirmed_at = db.Column(db.DateTime())
  roles = db.relationship('Role', secondary='roles_users',
                      backref=backref('user', lazy='dynamic'))
  rides = db.relationship('RideRequest', secondary='ride_request_users',
                      backref=backref('user', lazy='dynamic'))

  def set_password(self, plaintext):
    self.password = pbkdf2_sha256.hash(plaintext)

  def verify_password(self, plaintext):
    return pbkdf2_sha256.verify(plaintext, self.password)

  def is_active():
    return True

  def is_authenticated():
    return self.authenticated

  def is_anonymous():
    return False

  def get_id(self):
    return self.id

  def has_roles(self, *args):
    return set(args).issubset({role.name for role in self.roles})


class RideRequestsUsers(db.Model):
  """ """
  __tablename__ = 'ride_request_users'
  id = db.Column(db.Integer(), primary_key=True, unique=True)
  user_id = db.Column('user_id', db.Integer(), db.ForeignKey('user.id'))
  request_id = db.Column('request_id', db.Integer(), db.ForeignKey('ride_request.id'))


class RolesUsers(db.Model):
  """ Model """
  __tablename__ = 'roles_users'
  id = db.Column(db.Integer(), primary_key=True, unique=True)
  user_id = db.Column('user_id', db.Integer(), db.ForeignKey('user.id'))
  role_id = db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))


class CreditCard(db.Model):
  """ Credit Card Model """
  id = db.Column(Integer(), primary_key=True)
  __tablename__ = 'creditcard'
  card_number = db.Column(db.String(16))
  exp = db.Column(db.String(4))
  cvc = db.Column(db.String(5))
  zipcode = db.Column(db.String(5))


class ZipCode(db.Model):
  __tablename__ = 'zipcode'
  id = db.Column(db.Integer, primary_key=True, unique=True)
  zipcode = db.Column(db.String(5), unique=True)


