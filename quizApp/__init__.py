from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CsrfProtect
from flask_login import LoginManager
import os
import config

app = Flask(__name__)
login_manager = LoginManager(app)
csrf = CsrfProtect(app)
app.config.from_object(config.Config)
db = SQLAlchemy(app)

# These imports depend on app, above
import filters
import views
