"""Configurations for the project. These are loaded in
app.py.
"""

import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    """Global default config.
    """

    CSRF_ENABLED = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class Production(Config):
    """Configuration for production environments.
    """
    DEBUG = False
    TESTING = False

class Development(Config):
    """Configuration for development environments.
    """
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "mysql+mysqldb://quizapp:foobar@localhost/quizapp_test"
    SECRET_KEY = "Foobar"

class Testing(Config):
    """Config used for testing.
    """
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "mysql+mysqldb://quizapp:foobar@localhost/quizapp_test"
    SECRET_KEY = "Foobar"

configs = {
    "production": Production,
    "development": Development,
    "testing": Testing,
}
