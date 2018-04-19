
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

from flask_socketio import emit

from datetime import datetime
from fserver import app, login_manager, db, socketio
from models import User, Role, RideRequest
from forms import LoginForm, RegistrationForm, RideRequestForm, AcceptRideRequestForm


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
  """ Where user sends a ride request """
  form1 = RideRequestForm(prefix="form1") # from home to air port
  form2 = RideRequestForm(prefix="form2") # from air port to home
  # if home to airport is submitted
  if form1.validate_on_submit():
    datetime_now = datetime.now()
    current_user.rides.append(RideRequest(
      accepted=False,
      origin=form1.startLocation,
      destination=form1.endLocation,
      time_of_request=datetime_now,
      time_of_pickup=datetime_now,
      time_of_dropoff=datetime_now,
      group_ride=False,
      ))
    db.session.commit()
    return redirect(url_for('map',origin=form1.startLocation,destination=form1.endLocation))
  # if airport to home is submitted
  if form2.validate_on_submit():
    datetime_now = datetime.now()
    current_user.rides.append(RideRequest(
      accepted=False,
      origin=form2.startLocation,
      destination=form2.endLocation,
      time_of_request=datetime_now,
      time_of_pickup=datetime_now,
      time_of_dropoff=datetime_now,
      group_ride=False,
      ))
    db.session.commit()
    # swap origin, destination because of the way RideRequestForm is defined
    return redirect(url_for('map',origin=form2.endLocation,destination=form2.startLocation))

  # test to check for logged in drivers
  users = User.query.all()
  print 'Listing users'
  for u in users:
    print 'All drivers'
    if u.has_roles("driver"):
      print u.username
      print 'Logged in drivers'
      if u.is_logged_in():
        print u.username
      else:
        print 'None'
    else:
      print 'None'
  # before request
  return render_template('user_dashboard.html', form=form1, oform=form2, user=user, rides=current_user.rides)


@app.route('/driver_dashboard/<driver>', methods=['GET', 'POST'])
@driver_permission.require()
def driver_dashboard(driver):
  """ Display the requested rides where driver can accept """

  # get two customer requests
  users = User.query.filter(User.rides.any(accepted=False)).limit(2)

  try:
    user1 = users[0]
    user1_request = users[0].rides
  except Exception as e:
    user1 = None
    user1_request = None

  try:
    user2 = users[1]
    user2_request = users[1].rides
  except Exception as e:
    user2 = None
    user2_request = None


  # create Forms
  form1 = AcceptRideRequestForm(prefix="form1")
  form2 = AcceptRideRequestForm(prefix="form2")

  if form1.validate_on_submit():
    print "form 1 works"
    request = RideRequest.query.get(form1.request_id.data)
    request.accepted = True
    db.session.commit()
    print request
    #return redirect(url_for('map',origin=form2.endLocation,destination=form2.startLocation))

  if form2.validate_on_submit():
    print "form 2 works"
    request = RideRequest.query.get(form2.request_id.data)
    request.accepted = True
    db.session.commit()
    print request
    # return redirect(url_for('driver_dashboard', driver=driver, users=users,
    #   form1=form1, form2=form2))


  # if form.validate_on_submit():
  #   flash('Congratualtions, you made a request')
  #   return redirect(url_for('map',origin=form.startLocation,destination=form.endLocation))
  return render_template('driver_dashboard.html', driver=driver, users=users, u1=user1, u2=user2,
    r1=user1_request, r2=user2_request, form1=form1, form2=form2)

@app.route('/map', methods=['GET', 'POST'])
def map():
  """ Displays the map and directions of origin and destination """
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
      current_user.authenticated = True
      current_user.logged_in = True
      session['user_id'] = current_user.id
      
      # Tell Flask-Principal the identity changed
      identity_changed.send(current_app._get_current_object(),
                          identity=Identity(user.id))   

      # update the database
      db.session.add(current_user)
      db.session.commit()

      flash('Logged in successfully.')

      # if user is a user direct to userdashboard
      if current_user.has_roles("user"):
        return redirect(url_for('user_dashboard', user=current_user))

      # if user is a driver direct to driver dashboard
      if current_user.has_roles("driver"):
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
  current_user.logged_in = False
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


# SocketIO Functionality

def messageRecived():
  print( 'message was received!!!' )

@socketio.on( 'my event' )
def handle_my_custom_event( json ):
  print( 'recived my event: ' + str( json ) )
  socketio.emit( 'my response', json, callback=messageRecived )





