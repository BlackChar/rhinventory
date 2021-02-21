from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_github import GitHub
from flask_login import LoginManager

db = SQLAlchemy()
admin = Admin()
debug_toolbar = DebugToolbarExtension()
github = GitHub()
login_manager = LoginManager()