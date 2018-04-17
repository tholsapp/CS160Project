
from flask_script import Manager

from fserver import app, init_app, init_db

# Instanciate CLI Manager
climanager = Manager(app)

@climanager.command
def prime_database():
  init_db()

@climanager.command
def runserver(*args,**kwargs):
  """ Override default runser to init webapp before running """
  app = init_app()
  app.run(*args,**kwargs)

if __name__ == '__main__':
  climanager.run()
