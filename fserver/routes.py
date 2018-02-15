
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
from models import User
from forms import LoginForm, RegistrationForm


# Create a permission with a single Need, in this case a RoleNeed.
admin_permission = Permission(RoleNeed('admin'))
user_permission = Permission(RoleNeed('user'))
driver_permission = Permission(RoleNeed('driver'))


@app.route('/')
@app.route('/index')
def home():
  return render_template('home.html')

@app.route('/admin/dashboard')
@admin_permission.require()
def admin_dashboard():
  return "<h1>Only Admins can view this page</h1>"

@app.route('/user/dashboard')
@user_permission.require()
def user_dashboard():
  return "<h1>Only Users can view this page</h1>"

@app.route('/driver/dashboard')
@driver_permission.require()
def driver_dashboard():
  return "<h1>Only Drivers can view this page</h1>"

@app.route('/map')
def map():
  return render_template('map.html', title='Map')

@app.route('/register', methods=['GET', 'POST'])
def register():
  if current_user.is_authenticated:
    return redirect(url_for('home'))
  form = RegistrationForm()
  if form.validate_on_submit():
    db.session.add(User(username=form.username.data,
                      email=form.email.data,
                      password=pbkdf2_sha256.hash(form.password.data)))
    db.session.commit()
    flash('Congratulations, you are now a registered user!')
    return redirect(url_for('login'))
  return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    return redirect(url_for('home'))
  form = LoginForm()
  # Validate Login
  if form.validate_on_submit():
    user = User.query.filter_by(username=form.username.data).first()
    # Login and validate the user.
    if user is not None and user.password is not None \
        and user.verify_password(form.password.data):
      flash('Logged in successfully.')
      login_user(user,remember=form.remember_me.data)
      # Tell Flask-Principal the identity changed
      identity_changed.send(current_app._get_current_object(),
                          identity=Identity(user.id))
      return redirect(url_for('home'))
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
