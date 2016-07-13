"""Views for CRUD of activities.

In order to be as general as possible, each of the activity-specific views
tests the kind of activity it is loading and then defers to a more specific
function (for example, questions are read by read_question rather than
read_activity itself).
"""
from flask import Blueprint, render_template, url_for, jsonify, abort
from flask_security import roles_required
from sqlalchemy import not_

from quizApp.models import Activity, Dataset, Question, Choice
from quizApp.forms.experiments import get_question_form
from quizApp.forms.activities import QuestionForm, DatasetListForm,\
    ChoiceForm
from quizApp.forms.common import DeleteObjectForm
from quizApp import db

activities = Blueprint("activities", __name__, url_prefix="/activities")


@activities.route('/', methods=["GET"])
@roles_required("experimenter")
def read_activities():
    """Display a list of all activities.
    """
    activities_list = Activity.query.all()

    return render_template("activities/read_activities.html",
                           activities=activities_list)


@activities.route("/", methods=["PUT"])
@roles_required("experimenter")
def create_activity():
    """Create an activity.
    """
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

    create_choice_form = ChoiceForm(prefix="create")
    update_choice_form = ChoiceForm(prefix="update")

    delete_activity_form = DeleteObjectForm(prefix="activity")
    delete_choice_form = DeleteObjectForm(prefix="choice")

    return render_template("activities/settings_question.html",
                           question=question,
                           general_form=general_form,
                           dataset_form=dataset_form,
                           remove_dataset_mapping=remove_dataset_mapping,
                           add_dataset_mapping=add_dataset_mapping,
                           choices=question.choices,
                           create_choice_form=create_choice_form,
                           delete_activity_form=delete_activity_form,
                           delete_choice_form=delete_choice_form,
                           update_choice_form=update_choice_form)


@activities.route("/<int:activity_id>", methods=["POST"])
@roles_required("experimenter")
def update_activity(activity_id):
    """Update the activity based on transmitted form data.
    """
    activity = Activity.query.get(activity_id)

    if not activity:
        abort(404)

    if "question" in activity.type:
        return update_question(activity)


def update_question(question):
    """Given a question, update its settings.
    """
    general_form = QuestionForm()

    if general_form.validate():
        general_form.populate_question(question)
        db.session.commit()

        return jsonify({"success": 1})

    dataset_form = DatasetListForm()
    dataset_form.reset_objects()
    dataset_mapping = dataset_form.populate_objects(Dataset.query.all())

    if dataset_form.validate():
        for dataset_id in dataset_form.objects.data:
            dataset = dataset_mapping[dataset_id]

            if dataset in question.datasets:
                question.datasets.remove(dataset)
            else:
                question.datasets.append(dataset)

        db.session.commit()

        return jsonify({"success": 1})


@activities.route("/<int:activity_id>", methods=["DELETE"])
@roles_required("experimenter")
def delete_activity(activity_id):
    """Delete the given activity.
    """
    activity = Activity.query.get(activity_id)

    if not activity:
        abort(404)

    db.session.delete(activity)
    db.session.commit()

    next_url = url_for("activities.read_activities")

    return jsonify({"success": 1, "next_url": next_url})


@activities.route("/<int:question_id>/choices/", methods=["PUT"])
@roles_required("experimenter")
def create_choice(question_id):
    """Create a choice for the given question.
    """
    question = Question.query.get(question_id)

    if not question:
        abort(404)

    create_choice_form = ChoiceForm(prefix="create")

    if not create_choice_form.validate():
        abort(400)

    choice = Choice()

    create_choice_form.populate_choice(choice)

    choice.question_id = question.id

    choice.save()

    return jsonify({"success": 1})


@activities.route("/<int:question_id>/choices/<int:choice_id>",
                  methods=["POST"])
@roles_required("experimenter")
def update_choice(question_id, choice_id):
    """Update the given choice using form data.
    """
    question = Question.query.get(question_id)

    if not question:
        abort(404)

    choice = Choice.query.get(choice_id)

    if not choice:
        abort(404)

    if choice not in question.choices:
        abort(400)

    update_choice_form = ChoiceForm(prefix="update")

    if not update_choice_form.validate():
        abort(400)

    update_choice_form.populate_choice(choice)

    db.session.commit()

    return jsonify({"success": 1})


@activities.route("/<int:question_id>/choices/<int:choice_id>",
                  methods=["DELETE"])
@roles_required("experimenter")
def delete_choice(question_id, choice_id):
    """Delete the given choice.
    """
    question = Question.query.get(question_id)

    if not question:
        abort(404)

    choice = Choice.query.get(choice_id)

    if not choice:
        abort(404)

    if choice not in question.choices:
        abort(400)

    db.session.delete(choice)
    db.session.commit()

    return jsonify({"success": 1})
