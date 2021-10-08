from flask import render_template, flash, redirect, url_for, request, jsonify
from werkzeug.urls import url_parse
from flask_login import current_user, login_user, logout_user, login_required
from flask_babel import _, get_locale
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from app.models import User
from app.auth.email import send_password_reset_email

@bp.route('/login', methods=['GET','POST']) 
def login():
	# if logged in user navigates to login page redirect to index
	# current_user comes from flask-login
	if current_user.is_authenticated:
		return redirect(url_for('main.index'))
	form = LoginForm() 
   # parses the form data when the form is submitted.
	if form.validate_on_submit():
		# getting user from the database using username in the login form that was submitted
		# returns None if doesn't find user using query
		user = User.query.filter_by(username=form.username.data).first()
		# check_password from werkzeug
		# using a user object so it already contains the password_hash.
		# this function compares passed password to the password hash in the object
		if user is None or not user.check_password(form.password.data):
			flash(_('Invalid username or password'))
			return redirect(url_for('auth.login'))
		# function from flask-login that will put the user data and puts it in flask
		# and makes available the current_user variable 
		login_user(user, remember=form.remember_me.data)
		# request.args exposes content of query string in dictionary format
		next_page = request.args.get('next')
		# testing next_page to make sure only a relative path to this sight
		# if no next_page or if has a network location (not ''), ie a domain so not a relative path 
		# then pass to index because should only be going to this application
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('main.index')
		return redirect(next_page)
   # if the form hasn't been submitted then go to the form for it to be filled in.
	return render_template('auth/login.html', title=_('Sign In'), form=form)

@bp.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
   # if a logged in user then send to index
   if current_user.is_authenticated:
      return redirect(url_for('main.index'))
   form = RegistrationForm()
   if form.validate_on_submit():
      user = User(username=form.username.data, email=form.email.data)
      user.set_password(form.password.data)
      db.session.add(user)
      db.session.commit()
      flash(_('Congratulations, you are now a registered user!'))
      return redirect(url_for('auth.login'))
   return render_template('auth/register.html', title=_('Register'), form=form)


@bp.route('/reset_password_request', methods=['GET','POST'])
def reset_password_request():
   if current_user.is_authenticated:
      return redirect(url_for('main.index'))
   form = ResetPasswordRequestForm()
   if form.validate_on_submit():
      user = User.query.filter_by(email=form.email.data).first()
      if user:
         send_password_reset_email(user)
      flash(_('Check your email for the instructions to reset your password'))
      return redirect(url_for('auth.login'))
   return render_template('auth/reset_password_request.html', title=_('Reset Password'), form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
   if current_user.is_authenticated:
      return redirect(url_for('main.index'))
   user = User.verify_reset_password_token(token)
   if not user:
      return redirect(url_for('main.index'))
   form = ResetPasswordForm()
   if form.validate_on_submit():
      user.set_password(form.password.data)
      db.session.commit()
      flash(_('Your password has been reset.'))
      return redirect(url_for('auth.login'))
   return render_template('auth/reset_password.html', form=form)
