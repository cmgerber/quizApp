from flask import Flask
from flask_wtf.csrf import CsrfProtect
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import os
import config

login_manager = LoginManager()
db = SQLAlchemy()
csrf = CsrfProtect()

def create_app(config_name, overrides=None):
    global login_manager
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(config.configs[config_name])
    app.config.from_pyfile("instance_config.py", silent=True)
    if overrides:
        app.config.from_mapping(overrides)

    print "Using config: " + config_name

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from quizApp.views.admin import admin
    from quizApp.views.core import core
    from quizApp.views.experiments import experiments

    app.register_blueprint(admin)
    app.register_blueprint(core)
    app.register_blueprint(experiments)

    return app
