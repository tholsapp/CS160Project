
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

from datetime import datetime, timedelta
from fserver import app, login_manager, db
from models import User, Role, RideRequest
from forms import LoginForm, RegistrationForm, RideRequestForm, AcceptRideRequestForm
from directions_service import GMapDirectionService


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

@app.route('/user_dashboard/<user>', methods=['GET', 'POST'])
@user_permission.require()
def user_dashboard(user):
  """ Where user sends a ride request """
  form1 = RideRequestForm(prefix="form1") # from home to air port
  form2 = RideRequestForm(prefix="form2") # from air port to home  

  # if home to airport is submitted
  if form1.validate_on_submit():
    directions = GMapDirectionService(form1.startLocation, form1.endLocation)
    price =  15 + (directions.total_distance / (directions.total_duration)) + (0.05 * directions.total_duration)
    datetime_now = datetime.now()
    current_user.rides.append(RideRequest(
      user_id=current_user.id,
      accepted=True,
      is_active=False,
      user_origin=form1.startLocation,
      user_destination=form1.endLocation,
      price=str("%.2f" % price),
      time_of_request=datetime_now,
      time_of_pickup=datetime_now,
      time_of_dropoff=datetime_now,
      group_ride=False,
      ))
    db.session.commit()
    return redirect(url_for('accept_ride', rides=current_user.rides, price=str("%.2f" % price)))

  # if airport to home is submitted
  if form2.validate_on_submit():
    directions = GMapDirectionService(form2.endLocation, form2.startLocation)
    price =  15 + (directions.total_distance / (directions.total_duration)) + (0.05 * directions.total_duration)
    datetime_now = datetime.now()
    current_user.rides.append(RideRequest(
      user_id=current_user.id,
      accepted=True,
      is_active=False,
      user_origin=form2.endLocation,
      user_destination=form2.startLocation,
      price=str("%.2f" % price),
      time_of_request=datetime_now,
      time_of_pickup=datetime_now,
      time_of_dropoff=datetime_now,
      group_ride=False,
      ))
    db.session.commit()
    return redirect(url_for('accept_ride', rides=current_user.rides, price=str("%.2f" % price)))
  # before request
  return render_template('user_dashboard.html', form=form1, oform=form2, aform=None, rides=current_user.rides)


@app.route('/accept_ride', methods=['GET','POST'])
def accept_ride():
  form = AcceptRideRequestForm(prefix="form")
  rides = request.args.get('rides')
  price = request.args.get('price')
  # Displays after request has been made
  if request.method == "POST":
    print "form submitted"
    # get request id so we can look it up in the database
    request_id = 0
    for rrequest in current_user.rides:
      if rrequest.accepted and not rrequest.is_active:
        flash("A Driver has not accepted your request yet")
        return render_template('accept_ride.html', form=form, rides=current_user.rides, price=price)
      if rrequest.accepted and rrequest.is_active:
        request_id = rrequest.id
        break
       
    # check that request_id was found
    if request_id != 0:
    # look up most current instance of ride request
      rrequest = RideRequest.query.get(request_id)   
      dir1 = GMapDirectionService(rrequest.driver_origin, rrequest.user_origin)
      dir2 = GMapDirectionService(rrequest.user_origin, rrequest.user_destination)
      rrequest.accepted = False
      rrequest.is_active = False
      db.session.commit()

      return render_template('map.html', userid=current_user.id,
        uid=rrequest.user_id, did=rrequest.driver_id,
        dir1=dir1, dir2=dir2,
        uorigin=rrequest.user_origin, dorigin=rrequest.driver_origin, udestination=rrequest.user_destination,
        ply1=dir1.overview_path, ply2=dir2.overview_path,
        flag=rrequest.is_active)

  return render_template('accept_ride.html',form=form, rides=current_user.rides, price=price)


@app.route('/driver_dashboard/<driver>', methods=['GET', 'POST'])
@driver_permission.require()
def driver_dashboard(driver):
  """ Display the requested rides where driver can accept """

  # get two customer requests
  users = User.query.filter(User.rides.any(accepted=True, is_active=False)).limit(2)

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
    request = RideRequest.query.get(form1.request_id.data)
    request.driver_id = current_user.id
    request.driver_origin = current_user.location
    request.accepted = True
    request.is_active = True
    current_user.location = request.user_destination
    

    dir1 = GMapDirectionService(request.driver_origin, request.user_origin)
    dir2 = GMapDirectionService(request.user_origin, request.user_destination)
    request.time_of_pickup = datetime.now() + timedelta(seconds=dir1.total_duration);
    request.time_of_dropoff = datetime.now() + timedelta(seconds=dir1.total_duration) + timedelta(seconds=dir2.total_duration)  
    db.session.commit()
    return render_template('map.html', userid=current_user.id,
          uid=request.user_id, did=request.driver_id,
          dir1=dir1, dir2=dir2,
          uorigin=request.user_origin, dorigin=request.driver_origin, udestination=request.user_destination,
          ply1=dir1.overview_path, ply2=dir2.overview_path,
          flag=request.is_active)

  if form2.validate_on_submit():
    request = RideRequest.query.get(form2.request_id.data) 
    request.driver_id = current_user.id
    request.driver_origin = current_user.location
    request.time_of_pickup = datetime.now()
    request.accepted = True
    request.accepted = True
    request.is_active = True
    current_user.location = request.user_destination
    db.session.commit();

    dir1 = GMapDirectionService(request.driver_origin, request.user_origin)
    dir2 = GMapDirectionService(request.user_origin, request.user_destination)

    return render_template('map.html', userid=current_user.id,
          uid=request.user_id, did=request.driver_id,
          dir1=dir1, dir2=dir2,
          uorigin=request.user_origin, dorigin=request.driver_origin, udestination=request.user_destination,
          ply1=dir1.overview_path, ply2=dir2.overview_path,
          flag=request.is_active)

  return render_template('driver_dashboard.html', driver=driver, users=users, u1=user1, u2=user2,
    r1=user1_request, r2=user2_request, form1=form1, form2=form2)



@app.route('/map/<userid>', methods=['GET', 'POST'])
def map(userid):
  """ Displays the map and directions of origin and destination """
  uid = request.args['uid']
  did = request.args['did']
  dir1 = request.args['dir1']
  dir2 = request.args['dir2']
  uorigin = request.args['uorigin']
  dorigin = request.args['dorigin']
  udestination = request.args['udestination']
  ply1 = request.args['ply1']
  ply2 = request.args['ply2']
  flag = request.args['flag']

  return render_template('map.html', userid=userid,
    uid=uid, did=did,
    dir1=dir1, dir2=dir2, uorigin=uorigin,
    dorigin=dorigin, udestination=udestination,
    ply1=ply1, ply2=ply2, flag=flag)


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
    db.session.add(User(
      username=form.username.data,
      email=form.email.data,
      password=pbkdf2_sha256.hash(form.password.data),
      card_number=form.card_number.data,
      exp = form.exp_month.data + '/' + form.exp_year.data,
      cvc = form.cvc.data,
      zipcode = form.zipcode.data,
      roles=[Role.query.filter_by(name=form.role.data).first(),]
      ))
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





