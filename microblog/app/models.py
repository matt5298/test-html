from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db, login, app
from flask_login import UserMixin
from hashlib import md5
from time import time
import jwt

followers = db.Table('followers', db.Column('follower_id', db.Integer, db.ForeignKey('user.id')), db.Column('followed_id', db.Integer, db.ForeignKey('user.id')))

#this function return a user given the id
#decorator registers this function with flask-login
@login.user_loader
def load_user(id):
   # flask-login passes a string id so convert to an interger for database
   return User.query.get(int(id))

# UserMixin to support user functionality in flask_login 
# UserMixin adds is_anonymous property
class User(UserMixin, db.Model):
   id = db.Column(db.Integer, primary_key=True)
   username = db.Column(db.String(64), index=True, unique=True)
   email = db.Column(db.String(120), index=True, unique=True)
   password_hash = db.Column(db.String(128))
   # the backref=author specifies in this class the name of an attribute of the Post class
   # when I'm adding a post I use named argument 'author' instead of user_id.  Don't know if I can also use user_id.
   posts = db.relationship('Post', backref='author', lazy='dynamic')
   about_me = db.Column(db.String(140))
   last_seen = db.Column(db.DateTime, default=datetime.utcnow)
   # link user instaces to other user instances 
   # left side user is following the right side user.
   followed = db.relationship( 'User', secondary=followers, \
   primaryjoin=(followers.c.follower_id == id), \
   secondaryjoin=(followers.c.followed_id == id), \
   backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

   def __repr__(self):
      return '<User {}>'.format(self.username)
      #return 'User: ' + self.username

   def set_password(self, password):
      self.password_hash = generate_password_hash(password)

   def check_password(self, password):
      return check_password_hash(self.password_hash, password)

   def avatar(self, size):
      digest = md5(self.email.lower().encode('utf-8')).hexdigest()
      return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

   def follow(self, user):
      if not self.is_following(user):
         self.followed.append(user)

   def unfollow(self, user):
      if self.is_following(user):
         self.followed.remove(user)

   def is_following(self, user):
      return self.followed.filter(followers.c.followed_id == user.id).count() > 0

   def followed_posts(self):
      followed = Post.query.join( followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id) 
      own = Post.query.filter_by(user_id=self.id)
      return followed.union(own).order_by(Post.timestamp.desc())

   def get_reset_password_token(self, expires_in=600):
      return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in}, app.config['SECRET_KEY'], algorithm='HS256')

   @staticmethod
   def verify_reset_password_token(token):
      try:
         # jwt.decode returns dictionary that was encoded.
         # the 'reset_password' key in the decoded dictionary contains the user id
         id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
      except:
         return
      return User.query.get(id)

class Post(db.Model):
   # includes virtual field author from the relationship statement in User
   id = db.Column(db.Integer, primary_key=True)
   body = db.Column(db.String(140))
   timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
   user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

   def __repr__(self):
      return '<Post {}>'.format(self.body)


