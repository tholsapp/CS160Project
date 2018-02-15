
from sqlalchemy import create_engine

from flask_sqlalchemy import SQLAlchemy


# Initialize Flask-SQLAlchemy
db = SQLAlchemy()

def db_connection():
  return 'sqlite:///test.db'
