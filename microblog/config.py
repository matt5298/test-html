import os
import sys

basedir = os.path.abspath(os.path.dirname(__file__))
print('debug: '+ basedir, sys.stderr)
class Config(object):
   SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
   SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
      'sqlite:///' + os.path.join(basedir, 'app.db')
   SQLALCHEMY_TRACK_MODIFICATIONS = False
   SERVER_NAME= os.environ.get('MY_FLASK_SERVER')
   MAIL_SERVER = os.environ.get('MAIL_SERVER')
   MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
   MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') is not None
   MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
   MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
   ADMINS = ['matt5298@gmail.com']
   POSTS_PER_PAGE = 25 
   #LANGUAGES = ['en','es']
print('debug: End of config file', sys.stderr)
