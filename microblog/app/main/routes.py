from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from langdetect import detect, LangDetectException
from app import db
from app.main.forms import EditProfileForm, EmptyForm, PostForm, SearchForm
from app.models import User, Post
from app.translate import translate
from app.main import bp

@bp.before_app_request
def before_request():
   if current_user.is_authenticated:
      current_user.last_seen = datetime.utcnow()
      db.session.commit()
      g.search_form = SearchForm()
      g.locale = str(get_locale())

@bp.route('/', methods=['GET','POST'])
@bp.route('/index', methods=['GET','POST'])
@login_required
def index():
   form = PostForm()
   # detecting language of the post before saved to the database
   if form.validate_on_submit():
      try: 
         language = detect(form.post.data)
        #  print('debug language of post: ' + language)
      except LangDetectException:
          language = ''
      # creation of the post record object from the form data
      # author is the backref defined in User that refers to the user
      post = Post(body=form.post.data, author=current_user, language=language)
      db.session.add(post)
      db.session.commit()
      flash(_('Your post is now live!'))
      # Post/Redirect/Get pattern to avoid inserting duplicate posts when user refreshes browser
      # redirect here uses GET method.  This means last action by browser will be a GET and 
      # when user refreshes the page it will peform this action instead of the previous
      # POST which would have resubmitted the form data as well.
      return redirect(url_for('main.index'))
   page = request.args.get('page',1,type=int)
   # paginate SQLalchemy returns a pagination object.
   # paginationObject.items list of items from the query.
   posts = current_user.followed_posts().paginate(page, current_app.config['POSTS_PER_PAGE'], False)
   next_url = url_for('main.index', page=posts.next_num) \
      if posts.has_next else None
   prev_url = url_for('main.index', page=posts.prev_num) \
      if posts.has_prev else None
   return render_template('index.html',title=_('Home Page'), form=form, 
      posts=posts.items, next_url=next_url,
      prev_url=prev_url)

# <username> is a dynamic component and flask will accept anything in that position in the URL
# what ever is put in the place of username gets passed as the variable username
# login_required means this will only be accessible to a logged in user
@bp.route('/user/<username>')
@login_required
def user(username):
   user = User.query.filter_by(username=username).first_or_404()
   page = request.args.get('page', 1, type=int)
   # user.posts exists because of relationship defined in users with post.  So this represents an automatically generated query.
   posts = user.posts.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
   next_url = url_for('main.user', username=user.username, page=posts.next_num) \
      if posts.has_next else None
   prev_url = url_for('main.user', username=user.username, page=posts.prev_num) \
      if posts.has_prev else None
   form = EmptyForm()
   return render_template('user.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url, form=form) 

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
   form = EditProfileForm(current_user.username)
   # This is when the form is submitted so data needs to be saved to the database
   if form.validate_on_submit():
      current_user.username = form.username.data
      current_user.about_me = form.about_me.data
      db.session.commit()
      flash(_('Your changes have been saved.'))
      return redirect(url_for('main.edit_profile'))
   # This is when the form is first requested so fill with data from current_user
   elif request.method == 'GET':
      form.username.data = current_user.username
      form.about_me.data = current_user.about_me
   return render_template('edit_profile.html', title=_('Edit Profile'), form=form)

@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
   form = EmptyForm()
   if form.validate_on_submit():
      user = User.query.filter_by(username=username).first()
      if user is None:
         flash(_('User %(username)s not found.',username=username))
         return redirect(url_for('main.index'))
      if user == current_user:
         flash(_('you cannot follow yourself!'))
         return redirect(url_for('main.user', username=username))
      current_user.follow(user)
      db.session.commit()
      flash(_('You are following %(username)s!', username=username))
      return redirect(url_for('main.user', username=username))
   else:
      return redirect(url_for('main.index'))

@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
   form = EmptyForm()
   if form.validate_on_submit():
      user = User.query.filter_by(username=username).first()
      if user is None:
         flash(_('User %(username)s not found.', username=username))
         return redirect(url_for('main.index'))
      if user == current_user:
         flash(_('You cannot unfollow yourself!'))
         return redirect(url_for('main.user', username=username))
      current_user.unfollow(user)
      db.session.commit()
      flash(_('You are not following %(username)s.', username=username))
      return redirect(url_for('main.user', username=username))
   else:
      return redirect(url_for('main.index'))

@bp.route('/explore')
@login_required
def explore():
   page = request.args.get('page', 1, type=int)
   posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
   next_url = url_for('main.index', page=posts.next_num) \
      if posts.has_next else None
   prev_url = url_for('main.index', page=posts.prev_num) \
      if posts.has_prev else None
   return render_template('index.html',title=_('Explore'), 
      posts=posts.items, next_url=next_url,
      prev_url=prev_url)

#Used for search view function
@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page, 
            current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page -1) \
        if page > 1 else None
    return render_template('search.html', title=_('Search'), posts=posts, 
                            next_url=next_url, prev_url=prev_url)



# used for AJAX returns data not a rendered template
@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
    request.form['source_language'],
    request.form['dest_language'])})

