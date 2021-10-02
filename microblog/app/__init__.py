import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from logging.handlers import RotatingFileHandler
import os
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
# from flask_babel import Babel
from flask import request
#from  flask_babel import lazy_gettext as _l
import sys

print('debug: Start of __init__.py',sys.stderr)
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
# used by Flask-Login to know which view to redirect to if some one is not logged in.
#login.login_view = 'login'

#for language translation setting the login message and process it with the lazy
#tranlation function that will translate when used.
#by default the loginManager provides it's own login message
#login.login_message = _l('Please log in to access this page.')
#login.login_message = 'Please log in to access this page.'
mail = Mail(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
#babel = Babel(app)

if not app.debug:
   if app.config['MAIL_SERVER']:
      auth = None
      if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
         auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
      secure = None
      #if app.config['MAIL_USE_TLS']:
      #   secure = ()
      mail_handler = SMTPHandler(
         mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
         fromaddr='no-reply@' + app.config['MAIL_SERVER'],
         toaddrs=app.config['ADMINS'], subject='Microblog Failure',
         credentials=auth, secure=secure)
      mail_handler.setLevel(logging.ERROR)
      app.logger.addHandler(mail_handler)

# Want to start logging even if in debug mode.    
if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)

print ('Debug: starting app.logger',sys.stderr)
app.logger.setLevel(logging.INFO)
app.logger.info('Microblog startup')

#@babel.localeselector
#def get_locale():
#   return request.accept_languanges.best_match(app.config['LANGUANGES'])

from app import routes
