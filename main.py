#!/usr/bin/env python

import json
import os
try:
    from os import uname
except:
    def uname():
        return ['0', 'windows']

FLASK_APP_DIR = os.path.dirname(os.path.abspath(__file__))
MODE = 'local' # 'dev', 'prod'
GOOGLE_KEYS = json.load(open('private/google_auth_{}_flask.json'.format(MODE), 'r'))['web']

# Flask
from flask import Flask

app = Flask(__name__)

# Config
app.logger.info("Config: Production")
app.config.from_object('private.config.Config')

# Logging
import logging
logging.basicConfig(
    #filename="logs/flask-runestone.log",
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
    datefmt='%Y%m%d-%H:%M%p',
)

# Email on errors
"""
if not app.debug and not app.testing:
    import logging.handlers
    mail_handler = logging.handlers.SMTPHandler(
                        'localhost',
                        os.getenv('USER'),
                        app.config['SYS_ADMINS'],
                        '{0} error'.format(app.config['SITE_NAME'],
                        ),
                    )
    mail_handler.setFormatter(logging.Formatter('''
Message type:       %(levelname)s
Location:           %(pathname)s:%(lineno)d
Module:             %(module)s
Function:           %(funcName)s
Time:               %(asctime)s

Message:

%(message)s
    '''.strip()))
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)
    app.logger.info("Emailing on error is ENABLED")
else:
    app.logger.info("Emailing on error is DISABLED")"""

# Assets
from flask.ext.assets import Environment
assets = Environment(app)
# Ensure output directory exists
assets_output_dir = os.path.join(FLASK_APP_DIR, 'static', 'gen')
if not os.path.exists(assets_output_dir):
    os.mkdir(assets_output_dir)

# Email
"""from flask.ext.mail import Mail
mail = Mail(app)"""


# Google Authentication
from flask_oauthlib.client import OAuth
oauth = OAuth(app)
google = oauth.remote_app(
    'google',
    consumer_key=app.config.get('GOOGLE_ID'),
    consumer_secret=app.config.get('GOOGLE_SECRET'),
    request_token_params={
        'scope': 'https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

# Memcache
from werkzeug.contrib.cache import MemcachedCache
app.cache = MemcachedCache(app.config['MEMCACHED_SERVERS'])
def cache_fetch(key, value_function, timeout=None):
    '''Mimicking Rails.cache.fetch'''
    global app
    self = app.cache
    data = self.get(key)
    if data is None:
        data = value_function()
        self.set(key, data, timeout)
    return data
app.cache.fetch = cache_fetch

# Helpers
from helpers import datetimeformat
app.jinja_env.filters['datetimeformat'] = datetimeformat

# Business Logic
# http://flask.pocoo.org/docs/patterns/packages/
# http://flask.pocoo.org/docs/blueprints/
import controllers

from flask.ext.security import Security, SQLAlchemyUserDatastore
from models.models import db, Role, verify_instructor_status
from models.models import User, Course, CourseInstructors, Cohort

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore, register_form=ExtendedRegisterForm)

# Setup Admin
from flask.ext.admin import Admin, BaseView, expose
from flask.ext.admin.contrib.sqla import ModelView
from flask import g
from controllers.helpers import instructor_required
class AdminView(BaseView):
    @expose('/')
    def index(self):
        if self.is_accessible():
            return self.render('admin/index.html')
    def is_accessible(self):
        return g.user is None or not verify_instructor_status('compthink', g.user.id)
admin = Admin(app)
admin.add_view(ModelView(User, db.session, category='Tables'))
admin.add_view(ModelView(Course, db.session, category='Tables'))
admin.add_view(ModelView(CourseInstructors, db.session, category='Tables'))
admin.add_view(ModelView(Cohort, db.session, category='Tables'))

#from flask_application.controllers.admin import admin
#app.register_blueprint(admin)

