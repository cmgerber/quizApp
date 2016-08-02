"""These are views for interfacing with amazon mechanical turk.
"""

import random
import string

from flask import Blueprint, render_template, request, abort, redirect, \
    url_for

from quizApp.views.helpers import validate_model_id
from quizApp.models import Experiment, Participant
from flask_security.utils import encrypt_password
from flask_security import login_user

mturk = Blueprint("mturk", __name__, url_prefix="/mturk")


@mturk.route("/register")
def register():
    """Register this amturk user.

    From the URL arguments, grab the user ID from amazon and create a user
    record in our database. Log in the user. Redirect them to the experiment
    landing page.
    """
    try:
        experiment_id = request.args["experiment_id"]
    except KeyError:
        abort(400)

    experiment = validate_model_id(Experiment, experiment_id)

    if "workerId" in request.args:
        # The worker has accepted this HIT
        # Generate a new participant record
        password = ''.join(random.SystemRandom().
                           choice(string.ascii_uppercase + string.digits)
                           for _ in range(0, 15))

        participant = Participant(foreign_id=request.args["workerId"],
                                  email=request.args["workerId"],
                                  password=encrypt_password(password))
        participant.save()
        login_user(participant)

        return redirect(url_for("experiments.read_experiment",
                                experiment_id=experiment.id))

    return render_template("mturk/register.html", request=request,
                           experiment=experiment)
