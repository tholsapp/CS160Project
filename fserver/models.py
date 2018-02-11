
from passlib.hash import pbkdf2_sha256

from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Binary, Boolean, DateTime, Column, Integer, \
                       String, ForeignKey

from sqlalchemy.ext.hybrid import hybrid_property

#from passlib.hash import bcrypt

from fserver import apimanager, db, bcrypt

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
  roles = relationship('Role', secondary='roles_users',
                      backref=backref('users', lazy='dynamic'))

  #@hybrid_property
  #def _password(self):
  #  return self.password

  #@_password.setter
  def set_password(self, plaintext):
    self.password = pbkdf2_sha256.hash(plaintext)

  def verify_password(self, plaintext):
    return pbkdf2_sha256.verify(plaintext, self.password)
    #return bcrypt.check_password_hash(self.password, plaintext)

  def is_active():
    return True

  def is_authenticated():
    return self.authenticated

  def is_anonymous():
    return False

  def get_id(self):
    return self.id


# Create Endpoints
apimanager.create_api(User)
