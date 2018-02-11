from flask_script import Manager

from fserver import app, init_app

# Instanciate CLI Manager
climanager = Manager(app)

# Create a user to test with
#@app.before_first_request
#def create_user():
  #user_datastore.create_user(email='tester@testing.com', password='password')
  #db.session.add(User(username='test@testing.com',password='password'))
  #db.session.commit()
@climanager.command
def runserver(*args,**kwargs):
  """ Override default runser to init webapp before running """
  app = init_app()
  app.run(*args,**kwargs)

if __name__ == '__main__':
  climanager.run()
