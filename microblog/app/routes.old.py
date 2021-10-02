from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post
from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, PostForm, ResetPasswordRequestForm, ResetPasswordForm
from app.email import send_password_reset_email
from datetime import datetime
from flask_babel import _

varDebug = True

def debugURL():
    #troubleshooting url problems
    print("debug: " + request.root_url)
    print("debug: " + request.url)

@app.route('/<path:u_path>')
def catch_all(u_path):
    if varDebug:
        debugURL()
    print(repr(u_path))
    return repr(u_path)


@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
#@login_required
def index():
    if varDebug:
        deubgURL()
   form = PostForm()
   if form.validate_on_submit():
      # creation of the post record object from the form data
      # author is the backref defined in User that refers to the user
      post = Post(body=form.post.data, author=current_user)
      db.session.add(post)
      db.session.commit()
      flash(_('Your post is now live!'))
      # Post/Redirect/Get pattern to avoid inserting duplicate posts when user refreshes browser
      # redirect here uses GET method.  This means last action by browser will be a GET and 
      # when user refreshes the page it will peform this action instead of the previous
      # POST which would have resubmitted the form data as well.
      return redirect(url_for('index'))
   page = request.args.get('page',1,type=int)
   # paginate SQLalchemy returns a pagination object.
   # paginationObject.items list of items from the query.
   posts = current_user.followed_posts().paginate(page, app.config['POSTS_PER_PAGE'], False)
   next_url = url_for('index', page=posts.next_num) \
      if posts.has_next else None
   prev_url = url_for('index', page=posts.prev_num) \
      if posts.has_prev else None
   return render_template('index.html',title=_('Home Page'), form=form, 
      posts=posts.items, next_url=next_url,
      prev_url=prev_url)


@app.route('/login', methods=['GET','POST']) 
def login():
    if varDebug:
        deubgURL()
	# if logged in user navigates to login page redirect to index
	# current_user comes from flask-login
	if current_user.is_authenticated:
		return redirect(url_for('index'))
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
			return redirect(url_for('login'))
		# function from flask-login that will put the user data and puts it in flask
		# and makes available the current_user variable 
		login_user(user, remember=form.remember_me.data)
		# request.args exposes content of query string in dictionary format
		next_page = request.args.get('next')
		# testing next_page to make sure only a relative path to this sight
		# if no next_page or if has a network location (not ''), ie a domain so not a relative path 
		# then pass to index because should only be going to this application
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')
		return redirect(next_page)
   # if the form hasn't been submitted then go to the form for it to be filled in.
	return render_template('login.html', title=_('Sign In'), form=form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
   # if a logged in user then send to index
   if current_user.is_authenticated:
      return redirect(url_for('index'))
   form = RegistrationForm()
   if form.validate_on_submit():
      user = User(username=form.username.data, email=form.email.data)
      user.set_password(form.password.data)
      db.session.add(user)
      db.session.commit()
      flash(_('Congratulations, you are now a registered user!'))
      return redirect(url_for('login'))
   return render_template('register.html', title=_('Register'), form=form)

# <username> is a dynamic component and flask will accept anything in that position in the URL
# what ever is put in the place of username gets passed as the variable username
# login_required means this will only be accessible to a logged in user
@app.route('/user/<username>')
@login_required
def user(username):
   user = User.query.filter_by(username=username).first_or_404()
   page = request.args.get('page', 1, type=int)
   # user.posts exists because of relationship defined in users with post.  So this represents an automatically generated query.
   posts = user.posts.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
   next_url = url_for('user', username=user.username, page=posts.next_num) \
      if posts.has_next else None
   prev_url = url_for('user', username=user.username, page=posts.prev_num) \
      if posts.has_prev else None
   form = EmptyForm()
   return render_template('user.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url, form=form) 

@app.before_request
def before_request():
   if current_user.is_authenticated:
      current_user.last_seen = datetime.utcnow()
      db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
   form = EditProfileForm(current_user.username)
   # This is when the form is submitted so data needs to be saved to the database
   if form.validate_on_submit():
      current_user.username = form.username.data
      current_user.about_me = form.about_me.data
      db.session.commit()
      flash(_('Your changes have been saved.'))
      return redirect(url_for('edit_profile'))
   # This is when the form is first requested so fill with data from current_user
   elif request.method == 'GET':
      form.username.data = current_user.username
      form.about_me.data = current_user.about_me
   return render_template('edit_profile.html', title=_('Edit Profile'), form=form)

@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
   form = EmptyForm()
   if form.validate_on_submit():
      user = User.query.filter_by(username=username).first()
      if user is None:
         flash(_('User %(username)s not found.',username=username))
         return redirect(url_for('index'))
      if user == current_user:
         flash(_('you cannot follow yourself!'))
         return redirect(url_for('user', username=username))
      current_user.follow(user)
      db.session.commit()
      flash(_('You are following %(username)s!', username=username))
      return redirect(url_for('user', username=username))
   else:
      return redirect(url_for('index'))

@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
   form = EmptyForm()
   if form.validate_on_submit():
      user = User.query.filter_by(username=username).first()
      if user is None:
         flash(_('User %(username)s not found.', username=username))
         return redirect(url_for('index'))
      if user == current_user:
         flash(_('You cannot unfollow yourself!'))
         return redirect(url_for('user', username=username))
      current_user.unfollow(user)
      db.session.commit()
      flash(_('You are not following %(username)s.', username=username))
      return redirect(url_for('user', username=username))
   else:
      return redirect(url_for('index'))

@app.route('/explore')
@login_required
def explore():
   page = request.args.get('page', 1, type=int)
   posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
   next_url = url_for('index', page=posts.next_num) \
      if posts.has_next else None
   prev_url = url_for('index', page=posts.prev_num) \
      if posts.has_prev else None
   return render_template('index.html',title=_('Explore'), 
      posts=posts.items, next_url=next_url,
      prev_url=prev_url)

@app.route('/reset_password_request', methods=['GET','POST'])
def reset_password_request():
   if current_user.is_authenticated:
      return redirect(url_for('index'))
   form = ResetPasswordRequestForm()
   if form.validate_on_submit():
      user = User.query.filter_by(email=form.email.data).first()
      if user:
         send_password_reset_email(user)
      flash(_('Check your email for the instructions to reset your password'))
      return redirect(url_for('login'))
   return render_template('reset_password_request.html', title=_('Reset Password'), form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
   if current_user.is_authenticated:
      return redirect(url_for('index'))
   user = User.verify_reset_password_token(token)
   if not user:
      return redirect(url_for('index'))
   form = ResetPasswordForm()
   if form.validate_on_submit():
      user.set_password(form.password.data)
      db.session.commit()
      flash(_('Your password has been reset.'))
      return redirect(url_for('login'))
   return render_template('reset_password.html', form=form)

