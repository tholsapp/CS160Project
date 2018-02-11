from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from flask_login import LoginManager
from flask_restless import APIManager
from flask_bootstrap import Bootstrap

# Initialize Flask Application
app = Flask(__name__)
# Initialize Flask-Bootstrap
Bootstrap(app)
# Initialize Flask-SQLAlchemy
db = SQLAlchemy()
# Initialize Flask-Restless
apimanager = APIManager()
# Initialize Flask-LoginManager
login_manager = LoginManager()

def init_app():
  """ Configure app """
  app.config['DEBUG'] = True
  app.config['SECRET_KEY'] = 'super-secret'
  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  app.config['SECURITY_PASSWORD_SALT'] = ''

  # Setup Flask-SQLALchemy
  db.init_app(app)
  # Setup Flask-Login
  login_manager.init_app(app)
  login_manager.login_view =  "login"

  from models import User, Role
  # Setup Flask-Security
  user_datastore = SQLAlchemyUserDatastore(db, User, Role)
  security = Security(app, user_datastore)
  db.create_all()
  # Setup Flask-Restless
  apimanager.init_app(app, flask_sqlalchemy_db=db)

  return app;

import views
