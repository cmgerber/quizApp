from datetime import datetime
from random import shuffle
import os
import uuid

import flask
from flask import render_template, request, url_for, abort, current_app
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import text, func, select, and_, or_, not_, desc, bindparam
from flask_login import login_required, logout_user, login_user, current_user

from quizApp import db, login_manager
from quizApp import csrf
from quizApp import forms
from quizApp.models import Question, Choice, Participant, Graph, Experiment, \
        User, Assignment, ParticipantExperiment, Activity
