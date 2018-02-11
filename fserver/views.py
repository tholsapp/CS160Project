
from passlib.hash import pbkdf2_sha256


from flask import Flask, render_template, redirect, url_for, \
    flash, request, abort
from flask_login import current_user, login_user, \
    logout_user, login_required
from flask_security.utils import verify_password, encrypt_password
from werkzeug.urls import url_parse
from passlib.hash import bcrypt

from fserver import app, login_manager, db
from models import User
from forms import LoginForm, RegistrationForm


@app.route('/')
@app.route('/index')
@login_required
def home():
  return render_template('home.html')

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
  return redirect('login')

@login_manager.user_loader
def load_user(user_id):
  """ Callback used to reload the user object from
      the user ID stored in the session """
  return User.query.get(user_id)
