"""These are views for interfacing with amazon mechanical turk.
"""

import random
import string
import requests

from flask import Blueprint, render_template, request, abort, session
from flask import redirect, url_for
from sqlalchemy.orm.exc import NoResultFound

from quizApp.views.helpers import validate_model_id, get_first_assignment
from quizApp.models import Experiment, Participant
from quizApp import security
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

        try:
            participant = Participant.query.\
                filter_by(email=request.args["workerId"]).one()
        except NoResultFound:
            # Generate a new participant record
            password = ''.join(random.SystemRandom().
                               choice(string.ascii_uppercase + string.digits)
                               for _ in range(0, 15))

            participant = Participant(
                foreign_id=request.args["workerId"],
                email=request.args["workerId"],
                password=encrypt_password(password))
            security.datastore.add_role_to_user(participant, "participant")
            security.datastore.activate_user(participant)
            participant.save()
            session["experiment_post_finalize_handler"] = "mturk"
            session["mturk_assignmentId"] = request.args["assignmentId"]
            session["mturk_turkSubmitTo"] = request.args["turkSubmitTo"]

        login_user(participant)
        # get first assignment and send there

        return redirect(url_for("experiments.read_assignment",
                                a_id=get_first_assignment(experiment).id,
                                experiment_id=experiment.id))

    return render_template("mturk/register.html",
                           request=request,
                           experiment=experiment)


def submit_assignment():
    """Submit the current assignment back to amazon.
    """
    response = requests.post(
        session["mturk_turkSubmitTo"],
        data={"assignmentId": session["mturk_assignmentId"]})
    print response.status_code
