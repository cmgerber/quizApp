"""Views for CRUD of activities.

In order to be as general as possible, each of the activity-specific views
tests the kind of activity it is loading and then defers to a more specific
function (for example, questions are read by read_question rather than
read_activity itself).
"""

from flask import Blueprint, render_template, url_for, Markup, jsonify, abort
from flask_security import login_required, current_user, roles_required
from sqlalchemy import not_
import pdb

from quizApp.models import Activity, Dataset
from quizApp.forms.experiments import get_question_form
from quizApp.forms.activities import QuestionForm, DatasetListForm,\
    ChoiceListForm
from quizApp.forms.common import DeleteObjectForm

activities = Blueprint("activities", __name__, url_prefix="/activities")

@activities.route('/', methods=["GET"])
@roles_required("experimenter")
def read_activities():
    activities = Activity.query.all()

    return render_template("activities/read_activities.html",
                           activities=activities)


@activities.route("/", methods=["PUT"])
@roles_required("experimenter")
def create_activity():
    abort(404)


@activities.route("/<int:activity_id>", methods=["GET"])
@roles_required("experimenter")
def read_activity(activity_id):
    """Display a given activity as it would appear to a participant.
    """
    activity = Activity.query.get(activity_id)

    if not activity:
        abort(404)

    if "question" in activity.type:
        return read_question(activity)


def read_question(question):
    """Display a given question as it would appear to a participant.
    """
    form = get_question_form(question)

    form.populate_choices(question.choices)

    return render_template("activities/read_question.html",
                           question=question,
                           question_form=form)


@activities.route("/<int:activity_id>/settings", methods=["GET"])
@roles_required("experimenter")
def settings_activity(activity_id):
    """Display settings for a particular activity.
    """
    activity = Activity.query.get(activity_id)

    if not activity:
        abort(404)

    if "question" in activity.type:
        return settings_question(activity)


def settings_question(question):
    """Display settings for the given question.
    """
    general_form = QuestionForm()
    general_form.populate_fields(question)

    dataset_form = DatasetListForm()
    dataset_form.reset_objects()
    remove_dataset_mapping = dataset_form.populate_objects(question.datasets)
    add_dataset_mapping = dataset_form.populate_objects(
        Dataset.query.
        filter(not_(Dataset.questions.any(id=question.id))).all())

    choice_form = ChoiceListForm()
    choice_form.reset_objects()
    pdb.set_trace()
    choice_mapping = choice_form.populate_objects(question.choices)

    delete_form = DeleteObjectForm()

    return render_template("activities/settings_question.html",
                           question=question,
                           general_form=general_form,
                           dataset_form=dataset_form,
                           remove_dataset_mapping=remove_dataset_mapping,
                           add_dataset_mapping=add_dataset_mapping,
                           choice_form=choice_form,
                           choice_mapping=choice_mapping,
                           delete_form=delete_form
                           )


@activities.route("/<int:activity_id>", methods=["POST"])
@roles_required("experimenter")
def update_activity(activity_id):
    abort(404)


@activities.route("/<int:activity_id>", methods=["DELETE"])
@roles_required("experimenter")
def delete_activity(activity_id):
    abort(404)
