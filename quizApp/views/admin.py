from flask import current_app, Blueprint, render_template, flash, redirect, \
        url_for
from quizApp import db
from quizApp.forms.admin import LoginForm
from quizApp.models import User

admin = Blueprint('admin', __name__, url_prefix='/admin')
