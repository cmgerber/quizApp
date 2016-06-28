from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CsrfProtect
import os
import config

app = Flask(__name__)
csrf = CsrfProtect(app)
app.config.from_object(config.Production)
db = SQLAlchemy(app)

# These imports depend on app, above
import filters
import views
