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
    SQLALCHEMY_ECHO = True
    CSRF_ENABLED = True
    SECRET_KEY = "---"
    WTF_CSRF_METHODS=["POST","PUT","PATCH","DELETE"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "mysql+mysqldb://quizapp:foobar@localhost/quizapp"
