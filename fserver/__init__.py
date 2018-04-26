
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_security import Security, SQLAlchemyUserDatastore
from flask_principal import Principal, Permission, RoleNeed
from flask_restless import APIManager
from flask_bootstrap import Bootstrap
from passlib.hash import pbkdf2_sha256

from fserver.database import db, db_connection
from fserver.models import User, Role, Zipcode
import pandas as pd
import itertools
import csv

# Initialize Flask Application
app = Flask(__name__)
# Initialize Flask-Bootstrap
Bootstrap(app)
# Initialize Flask-Restless
apimanager = APIManager()
# Initialize Flask-LoginManager
login_manager = LoginManager()
# Initialize Flask-Principal
principal_manager = Principal(app)


def init_app():
  """ Configure app """
  app.config['DEBUG'] = True
  app.config['THREADED'] = True
  app.config['PROCESSES'] = 3
  app.config['USE_RELOADER'] = True
  app.config['SECRET_KEY'] = 'abc'
  app.config['SQLALCHEMY_DATABASE_URI'] = db_connection()
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  app.config['SECURITY_PASSWORD_SALT'] = ''

  # Setup Flask-SQLALchemy
  db.init_app(app)
  # Setup Flask-Login
  login_manager.init_app(app)
  login_manager.login_view =  "login"

  # Setup Flask-Security
  user_datastore = SQLAlchemyUserDatastore(db, User, Role)
  security = Security(app, user_datastore)
  # Create all tables in database
  db.create_all()
  db.session.commit()
  # Setup Flask-Restless
  apimanager.init_app(app, flask_sqlalchemy_db=db)

  return app;

def init_db():
  """ Set up database with test users """
  app = init_app()
  if not Role.query.filter_by(name='admin').first() and \
      not Role.query.filter_by(name='user').first() and \
      not Role.query.filter_by(name='driver').first():

    admin_role = Role(name='admin',description='')
    user_role = Role(name='user',description='')
    driver_role = Role(name='driver',description='')
    db.session.add(admin_role)
    db.session.add(user_role)
    db.session.add(driver_role)
    db.session.commit()

  if not User.query.filter_by(username='user1').first():
    user1 = User(username='user1',
        email='user1@gmail.com',
        password=pbkdf2_sha256.hash('password'),
        card_number = '1134567812345678',
        exp = '01/2020',
        cvc = '123',
        zipcode = '95050'
        )
    user1.roles = [user_role,]
    db.session.add(user1)

  if not User.query.filter_by(username='user2').first():
    user2 = User(username='user2',
        email='user2@gmail.com',
        password=pbkdf2_sha256.hash('password'),
        card_number = '2234567812345678',
        exp = '01/2020',
        cvc = '123',
        zipcode = '95050'
        )
    user2.roles = [user_role,]
    db.session.add(user2)

  if not User.query.filter_by(username='driver1').first():
    driver1 = User(username='driver1',
        email='driver1@gmail.com',
        password=pbkdf2_sha256.hash('password'),
        location='500 El Camino Real, Santa Clara, CA 95053',    
        card_number = '3334567812345678',
        exp = '01/2020',
        cvc = '123',
        zipcode = '95050',
        )
    driver1.roles = [driver_role,]
    db.session.add(driver1)

  if not User.query.filter_by(username='driver2').first():
    driver2 = User(username='driver2',
        email='driver2@gmail.com',
        password=pbkdf2_sha256.hash('password'),
        location='1 Washington Sq, San Jose, CA 95192',
        card_number = '4434567812345678',
        exp = '01/2020',
        cvc = '123',
        zipcode = '95050'
        )
    driver2.roles = [driver_role,]
    db.session.add(driver2)

  colnames = ['zip_code', 'latitude', 'longitude', 'city', 'state', 'county']
  data = pd.read_csv('fserver/static/zip_codes_states.csv', names=colnames)

  zipcodes = data.zip_code.tolist()
  counties = data.county.tolist()
  
  for z,c in itertools.izip_longest(zipcodes,counties):
    if c == 'Santa Clara' or \
       c == 'San Mateo' or \
       c == 'Alameda':
        if not Zipcode.query.filter_by(zipcode=z).first():
          db.session.add(Zipcode(zipcode=z, county=c))


  db.session.commit()

  x = Zipcode.query.all()
  for y in x:
    print y.zipcode

""" Circular Import """
import routes
