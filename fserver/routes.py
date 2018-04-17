
from passlib.hash import pbkdf2_sha256


from flask import Flask, session, render_template, redirect, url_for, \
    current_app, flash, request, abort
from flask_login import current_user, login_user, \
    logout_user, login_required
from flask_principal import Permission, RoleNeed, Identity, AnonymousIdentity, \
     identity_changed
from flask_security.utils import verify_password, encrypt_password
from werkzeug.urls import url_parse
from passlib.hash import bcrypt

from fserver import app, login_manager, db
from models import User, Role
from forms import LoginForm, RegistrationForm, RideRequestForm


# Create a permission with a single Need, in this case a RoleNeed.
admin_permission = Permission(RoleNeed('admin'))
user_permission = Permission(RoleNeed('user'))
driver_permission = Permission(RoleNeed('driver'))

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def home():
  return render_template('home.html')

@app.route('/about')
def about():
  return "about"

# @app.route('/dashboard')
# @admin_permission.require()
# def admin_dashboard():
#   return "<h1>Only Admins can view this page</h1>"

@app.route('/user_dashboard/<user>', methods=['GET', 'POST'])
@user_permission.require()
def user_dashboard(user):
  """  """
  form1 = RideRequestForm(prefix="form1") # from home to air port
  form2 = RideRequestForm(prefix="form2") # from air port to home
  if form1.validate_on_submit():
    flash('Congratualtions, you made a request')
    print 'form 1 called'
    return redirect(url_for('map',origin=form1.startLocation,destination=form1.endLocation))
  # swap origin, destination because of the way RideRequestForm is defined
  if form2.validate_on_submit():
    flash('Congratualtions, you made a request')
    print 'for 2 called'
    return redirect(url_for('map',origin=form2.endLocation,destination=form2.startLocation))
  # before request
  return render_template('user_dashboard.html', form=form1, oform=form2, user=user)


@app.route('/driver_dashboard/<driver>')
@driver_permission.require()
def driver_dashboard(driver):
  # if form.validate_on_submit():
  #   flash('Congratualtions, you made a request')
  #   return redirect(url_for('map',origin=form.startLocation,destination=form.endLocation))
  return render_template('driver_dashboard.html', driver=driver)

@app.route('/map', methods=['GET', 'POST'])
def map():
  """  """
  if request.method == 'GET':
    origin = request.args['origin']
    destination = request.args['destination']
    return render_template('map.html', origin=origin,destination=destination)
  return render_template('map.html')

@app.route('/request-ride', methods=['GET', 'POST'])
def request_ride():
  if request.method == 'POST':
    return redirect(url_for('home'))
  return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
  """  """
  if current_user.is_authenticated:
    return redirect(url_for('home'))
  form = RegistrationForm()
  if form.validate_on_submit():
    db.session.add(User(username=form.username.data,
                      email=form.email.data,
                      password=pbkdf2_sha256.hash(form.password.data),
                      roles=[Role.query.filter_by(name=form.role.data).first(),]))
    db.session.commit()
    flash('Congratulations, you are now a registered user!')
    return redirect(url_for('login'))
  return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
  """  """
  if current_user.is_authenticated:
    return redirect(url_for('home'))
  form = LoginForm()
  # Validate Login
  if form.validate_on_submit():
    user = User.query.filter_by(username=form.username.data).first()
    # Login and validate the user.
    if user is not None and user.password is not None \
        and user.verify_password(form.password.data):
      login_user(user, remember=False)
      session['user_id'] = current_user.id
      
      # Tell Flask-Principal the identity changed
      identity_changed.send(current_app._get_current_object(),
                          identity=Identity(user.id))   

      # update the database
      db.session.add(current_user)
      db.session.commit()

      flash('Logged in successfully.')
      for r in current_user.roles:
        # check if user is a user
        role = Role.query.filter_by(name='user').first()
        if r == role:
          return redirect(url_for('user_dashboard', user=current_user))

        # check if user is a driver
        role = Role.query.filter_by(name='driver').first()
        if r == role:
          return redirect(url_for('driver_dashboard', driver=current_user))
    else:
      flash('Invalid username or passowrd')
      return redirect(url_for('login'))
  return render_template('login.html', title='Sign In', form=form)

@app.route("/logout", methods=["GET"])
@login_required
def logout():
  """Logout the current user."""
  current_user.authenticated = False
  db.session.add(current_user)
  db.session.commit()
  logout_user()

  # Remove session keys set by Flask-Principal
  for key in ('identity.name', 'identity.auth_type'):
      session.pop(key, None)

  # Tell Flask-Principal the user is anonymous
  identity_changed.send(current_app._get_current_object(),
                      identity=AnonymousIdentity())

  return redirect('login')

@login_manager.user_loader
def load_user(user_id):
  """ Callback used to reload the user object from
      the user ID stored in the session """
  return User.query.get(user_id)


