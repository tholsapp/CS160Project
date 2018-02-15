from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_security import Security, SQLAlchemyUserDatastore
from flask_principal import Principal
from flask_restless import APIManager
from flask_bootstrap import Bootstrap
from passlib.hash import pbkdf2_sha256

from fserver.database import db, db_connection
from fserver.models import User, Role

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
  app.config['SECRET_KEY'] = 'super-secret'
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

  if not User.query.filter_by(username='admin').first():
    admin = User(username='admin',
        email='admin@gmail.com',
        password=pbkdf2_sha256.hash('super-secret')
        )
    admin.roles = [admin_role,]
    db.session.add(admin)

  if not User.query.filter_by(username='user1').first():
    user1 = User(username='user1',
        email='user1@gmail.com',
        password=pbkdf2_sha256.hash('password')
        )
    user1.roles = [user_role,]
    db.session.add(user1)

  if not User.query.filter_by(username='user2').first():
    user2 = User(username='user2',
        email='user2@gmail.com',
        password=pbkdf2_sha256.hash('password')
        )
    user2.roles = [user_role,]
    db.session.add(user2)

  if not User.query.filter_by(username='driver1').first():
    driver1 = User(username='driver1',
        email='driver1@gmail.com',
        password=pbkdf2_sha256.hash('password')
        )
    driver1.roles = [driver_role,]
    db.session.add(driver1)

  if not User.query.filter_by(username='driver2').first():
    driver2 = User(username='driver2',
        email='driver2@gmail.com',
        password=pbkdf2_sha256.hash('password')
        )
    driver2.roles = [driver_role,]
    db.session.add(driver2)

  db.session.commit()


import routes
