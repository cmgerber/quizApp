from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CsrfProtect
import os
import config

app = Flask(__name__, instance_relative_config=True)
# Default to development config
env = os.environ.get("APP_CONFIG", "development")
app.config.from_object(config.configs[env])
app.config.from_pyfile("config.py", silent=True)

print "Using config: " + env

csrf = CsrfProtect(app)
db = SQLAlchemy(app)

# These imports depend on app, above
import filters
import views
