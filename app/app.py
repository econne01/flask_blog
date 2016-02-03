""" Configuration for Flask app """
import os
import urllib

from flask import (Flask, abort, flash, Response)
from playhouse.flask_utils import FlaskDB


ADMIN_PASSWORD = 'secret'
APP_DIR = os.path.dirname(os.path.realpath(__file__))
DATABASE = 'sqliteext:///%s' % os.path.join(APP_DIR, 'blog.db')
DEBUG = False
SECRET_KEY = 'shhh, secret!'  # Used by Flask to encrypt session cookie.
SITE_WIDTH = 800


app = Flask(__name__)
app.config.from_object(__name__)

flask_db = FlaskDB(app)
database = flask_db.database

from models import Entry, FTSEntry
database.create_tables([Entry, FTSEntry], safe=True)


# Setup routes
import views
app.add_url_rule('/login/', 'login', views.login, methods=['GET', 'POST'])
app.add_url_rule('/logout/',  'logout', views.logout, methods=['GET', 'POST'])
app.add_url_rule('/', 'index', views.index, methods=['GET'])
app.add_url_rule('/create', 'create', views.create, methods=['GET', 'POST'])
app.add_url_rule('/drafts', 'drafts', views.drafts, methods=['GET'])
app.add_url_rule('/<slug>', 'detail', views.detail, methods=['GET'])
app.add_url_rule('/<slug>/edit', 'edit', views.edit, methods=['GET', 'POST'])


@app.template_filter('clean_querystring')
def clean_querystring(request_args, *keys_to_remove, **new_values):
    querystring = dict((key, value) for key, value in request_args.items())
    for key in keys_to_remove:
        querystring.pop(key, None)
    querystring.update(new_values)
    return urllib.urlencode(querystring)

@app.errorhandler(404)
def not_found(exc):
    return Response('<h3>404 Error: Page Not found</h3>'), 404

