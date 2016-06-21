"""Configurations for the project. These are loaded in
app.py.
"""

import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    """Global default config.
    """

    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = "---"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///quizDB.db"
