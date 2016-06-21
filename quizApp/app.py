from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import config

app = Flask(__name__)
app.config.from_object(config.Config)
db = SQLAlchemy(app)
