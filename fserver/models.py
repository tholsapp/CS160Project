
from passlib.hash import pbkdf2_sha256

from flask_security import UserMixin, RoleMixin
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Binary, Boolean, DateTime, Column, Integer, \
                       String, ForeignKey

from fserver.database import db

class RolesUsers(db.Model):
  __tablename__ = 'roles_users'
  id = db.Column(db.Integer(), primary_key=True)
  user_id = db.Column('user_id', db.Integer(), db.ForeignKey('user.id'))
  role_id = db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))

class Role(db.Model, RoleMixin):
  __tablename__ = 'role'
  id = db.Column(Integer(), primary_key=True)
  name = db.Column(db.String(80), unique=True)
  description = db.Column(db.String(255))

class User(db.Model, UserMixin):
  __tablename__ = 'user'
  id = db.Column(db.Integer, primary_key=True, unique=True)
  email = db.Column(db.String(255), unique=True)
  username = db.Column(db.String(64), unique=True)
  password = db.Column(db.String(255))
  last_login_at = db.Column(db.DateTime())
  current_login_at = db.Column(db.DateTime())
  last_login_ip = db.Column(db.String(100))
  current_login_ip = Column(db.String(100))
  login_count = db.Column(db.Integer())
  confirmed_at = db.Column(db.DateTime())
  roles = db.relationship('Role', secondary='roles_users',
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


