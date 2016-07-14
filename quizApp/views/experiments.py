"""Views that handle CRUD for experiments and rendering questions for
participants.
"""
from collections import defaultdict
from datetime import datetime
import json
import os

from flask import Blueprint, render_template, url_for, Markup, jsonify, \
    abort, current_app
from flask_security import login_required, current_user, roles_required
from sqlalchemy import not_
from sqlalchemy.orm.exc import NoResultFound

from quizApp import db
from quizApp.forms.common import DeleteObjectForm
from quizApp.forms.experiments import CreateExperimentForm, ActivityListForm, \
    get_question_form
from quizApp.models import Question, Choice, Experiment, Assignment, \
    ParticipantExperiment, Activity, Participant


experiments = Blueprint("experiments", __name__, url_prefix="/experiments")


def validate_model_id(model, model_id, code=404):
    """Given a model and id, retrieve and return that model from the database
    or abort with the given code.
    """
    obj = model.query.get(model_id)

    if not obj:
        abort(code)

    return obj


def get_participant_experiment_or_abort(exp_id, code=400):
    """Return the ParticipantExperiment object corresponding to the current
    user and exp_id or abort with the given code.
    """
    try:
        return ParticipantExperiment.query.\
            filter_by(participant_id=current_user.id).\
            filter_by(experiment_id=exp_id).one()
    except NoResultFound:
        abort(code)


@experiments.route('/', methods=["GET"])
@login_required
def read_experiments():
    """List experiments.
    """
    exps = Experiment.query.all()
    create_form = CreateExperimentForm()

    return render_template("experiments/read_experiments.html",
                           experiments=exps, create_form=create_form)


@experiments.route("/", methods=["POST"])
@roles_required("experimenter")
def create_experiment():
    """Create an experiment and save it to the database.
    """
    form = CreateExperimentForm()
    if not form.validate_on_submit():
        abort(400)

    exp = Experiment(
        name=form.name.data,
        start=form.start.data,
        stop=form.stop.data,
        created=datetime.now())

    exp.save()

    return render_template("experiments/create_experiment_response.html",
                           exp=exp)


@experiments.route('/<int:exp_id>', methods=["GET"])
@login_required
def read_experiment(exp_id):
    """View the landing page of an experiment, along with the ability to start.
    """
    exp = validate_model_id(Experiment, exp_id)

    part_exp = get_participant_experiment_or_abort(exp_id)

    if len(part_exp.assignments) == 0:
        assignment = None
    elif part_exp.complete:
        assignment = part_exp.assignments[0]
    else:
        try:
            assignment = part_exp.assignments[part_exp.progress]
        except IndexError:
            assignment = part_exp.assignments[0]

    return render_template("experiments/read_experiment.html", experiment=exp,
                           assignment=assignment)


@experiments.route("/<int:exp_id>", methods=["DELETE"])
@roles_required("experimenter")
def delete_experiment(exp_id):
    """Delete an experiment.
    """
    exp = validate_model_id(Experiment, exp_id)

    db.session.delete(exp)
    db.session.commit()

    return jsonify({"success": 1, "next_url":
                    url_for('experiments.read_experiments')})


@experiments.route("/<int:exp_id>/activities", methods=["PUT"])
@roles_required("experimenter")
def update_experiment_activities(exp_id):
    """Change what activities are contained in an experiment.
    """
    exp = validate_model_id(Experiment, exp_id)

    activities_update_form = ActivityListForm()

    activities_pool = Activity.query.all()

    activities_mapping = activities_update_form.\
        populate_activities(activities_pool)

    if not activities_update_form.validate():
        abort(400)

    for activity_id in activities_update_form.activities.data:
        activity = activities_mapping[activity_id]
        if exp in activity.experiments:
            activity.experiments.remove(exp)
        else:
            activity.experiments.append(exp)

    db.session.commit()
    return jsonify({"success": 1})


@experiments.route("/<int:exp_id>", methods=["PUT"])
@roles_required("experimenter")
def update_experiment(exp_id):
    """Modify an experiment's properties.
    """
    exp = validate_model_id(Experiment, exp_id)

    experiment_update_form = CreateExperimentForm()

    if not experiment_update_form.validate():
        abort(400)

    exp.name = experiment_update_form.name.data
    exp.start = experiment_update_form.start.data
    exp.stop = experiment_update_form.stop.data

    exp.save()

    return jsonify({"success": 1})


@experiments.route('/<int:exp_id>/assignment/<int:a_id>')
@roles_required("participant")
def read_assignment(exp_id, a_id):
    """Given an assignment ID, retrieve it from the database and display it to
    the user.
    """
    experiment = validate_model_id(Experiment, exp_id)
    assignment = validate_model_id(Assignment, a_id)

    part_exp = get_participant_experiment_or_abort(exp_id)

    if assignment not in part_exp.assignments:
        abort(400)

    activity = validate_model_id(Activity, assignment.activity_id)

    if "question" in activity.type:
        return read_question(experiment, activity, assignment)

    abort(404)


def read_question(experiment, question, assignment):
    """Retrieve a question from the database and render its template.

    This function assumes that all necessary error checking has been done on
    its parameters.
    """

    question_form = get_question_form(question)
    question_form.populate_choices(question.choices)

    if assignment.choice_id:
        question_form.choices.default = str(assignment.choice_id)
        question_form.process()

    question_form.reflection.data = assignment.reflection

    part_exp = assignment.participant_experiment
    this_index = part_exp.assignments.index(assignment)

    if not part_exp.complete:
        # If the participant is not done, then save the choice order
        choice_order = [c.id for c in question.choices]
        assignment.choice_order = json.dumps(choice_order)
        assignment.save()
        next_url = None
        explanation = ""
    else:
        # If the participant is done, have a link right to the next question
        next_url = get_next_assignment_url(part_exp, this_index)
        explanation = question.explanation

    previous_assignment = None

    if this_index - 1 > -1:
        previous_assignment = part_exp.assignments[this_index - 1]

    return render_template("experiments/read_question.html", exp=experiment,
                           question=question, assignment=assignment,
                           mc_form=question_form,
                           next_url=next_url,
                           explanation=explanation,
                           experiment_complete=part_exp.complete,
                           previous_assignment=previous_assignment)


@experiments.route('/<int:exp_id>/assignments/<int:a_id>', methods=["POST"])
def update_assignment(exp_id, a_id):
    """Record a user's answer to this assignment
    """
    assignment = validate_model_id(Assignment, a_id)
    question = validate_model_id(Question, assignment.activity_id)
    part_exp = assignment.participant_experiment
    validate_model_id(Experiment, exp_id)

    if part_exp.complete:
        abort(400)

    if "question" not in assignment.activity.type:
        # Pass for now
        return jsonify({"success": 1})

    question_form = get_question_form(question)
    question_form.populate_choices(question.choices)

    if not question_form.validate():
        return jsonify({"success": 0})

    selected_choice = validate_model_id(Choice,
                                        int(question_form.choices.data), 400)

    # User has answered this question successfully
    this_index = part_exp.assignments.index(assignment)
    assignment.choice_id = selected_choice.id
    assignment.reflection = question_form.reflection.data

    if this_index == part_exp.progress:
        part_exp.progress += 1

    next_url = get_next_assignment_url(part_exp, this_index)

    db.session.commit()
    return jsonify({"success": 1, "next_url": next_url})


def get_next_assignment_url(participant_experiment, current_index):
    """Given an experiment, a participant_experiment, and the current index,
    find the url of the next assignment in the sequence.
    """
    experiment_id = participant_experiment.experiment.id
    try:
        # If there is a next assignment, return its url
        next_url = url_for(
            "experiments.read_assignment",
            exp_id=experiment_id,
            a_id=participant_experiment.assignments[current_index + 1].id)
    except IndexError:
        next_url = None

    if not next_url:
        # We've reached the end of the experiment
        if not participant_experiment.complete:
            # The experiment needs to be submitted
            next_url = url_for("experiments.confirm_done_experiment",
                               exp_id=experiment_id)
        else:
            # Experiment has already been submitted
            next_url = url_for("experiments.read_experiment",
                               exp_id=experiment_id)

    return next_url

@experiments.route('/<int:exp_id>/settings', methods=["GET"])
@roles_required("experimenter")
def settings_experiment(exp_id):
    """Give information on an experiment and its activities.
    """
    experiment = validate_model_id(Experiment, exp_id)

    # Due to an unfortunate quirk in wtforms, we can't use two separate forms
    # for the two lists of activities on this page because they both will have
    # the same set of choices. So what we do instead is have one form but two
    # mappings, one mapping for activities in the exp and one for not in the
    # exp. We then render two forms based on what is in each mapping.

    update_experiment_form = CreateExperimentForm()

    activities_form = ActivityListForm()
    activities_form.reset_activities()
    remove_activities_mapping = activities_form.populate_activities(
        experiment.activities)

    add_activities_mapping = activities_form.populate_activities(
        Activity.query.
        filter(not_(Activity.experiments.any(id=experiment.id))).all())

    delete_experiment_form = DeleteObjectForm()

    return render_template("experiments/settings_experiment.html",
                           experiment=experiment,
                           update_experiment_form=update_experiment_form,
                           activities_form=activities_form,
                           add_activities_mapping=add_activities_mapping,
                           remove_activities_mapping=remove_activities_mapping,
                           delete_experiment_form=delete_experiment_form)


def get_question_stats(assignment, question_stats):
    """Given an assignment of a question and a stats array, return statistics
    about this question in the array.
    """
    question = assignment.activity
    question_stats[question.id]["question_text"] = question.question

    if assignment.choice:
        try:
            question_stats[question.id]["num_responses"] += 1
        except KeyError:
            question_stats[question.id]["num_responses"] = 1

        if assignment.choice.correct:
            try:
                question_stats[question.id]["num_crrect"] += 1
            except KeyError:
                question_stats[question.id]["num_correct"] = 1


@experiments.route("/<int:exp_id>/results", methods=["GET"])
@roles_required("experimenter")
def results_experiment(exp_id):
    """Render some results.
    """
    experiment = validate_model_id(Experiment, exp_id)

    num_participants = Participant.query.count()
    num_finished = ParticipantExperiment.query.\
        filter_by(experiment_id=experiment.id).\
        filter_by(progress=-1).count()

    percent_finished = num_finished / float(num_participants)

    # {"question_id": {"question": "question_text", "num_responses":
    #   num_responses, "num_correct": num_correct], ...}
    question_stats = defaultdict(dict)

    for assignment in experiment.assignments:
        activity = assignment.activity

        if "question" in activity.type:
            get_question_stats(assignment, question_stats)

    return render_template("experiments/results_experiment.html",
                           experiment=experiment,
                           num_participants=num_participants,
                           num_finished=num_finished,
                           percent_finished=percent_finished,
                           question_stats=question_stats)


@experiments.route("/<int:exp_id>/confirm_done", methods=["GET"])
@roles_required("participant")
def confirm_done_experiment(exp_id):
    """Show the user a page before finalizing their quiz answers.
    """
    experiment = validate_model_id(Experiment, exp_id)

    return render_template("experiments/experiment_confirm_done.html",
                           experiment=experiment)


@experiments.route("/<int:exp_id>/finalize", methods=["GET"])
@roles_required("participant")
def finalize_experiment(exp_id):
    """Finalize the user's answers for this experiment. They will no longer be
    able to edit them, but may view them.
    """
    validate_model_id(Experiment, exp_id)
    part_exp = get_participant_experiment_or_abort(exp_id)

    part_exp.complete = True

    db.session.commit()

    return render_template("experiments/experiment_finalize.html")


@experiments.app_template_filter("datetime_format")
def datetime_format_filter(value, fmt="%Y-%m-%d %H:%M:%S"):
    """Format the value (a datetime) according to fmt with strftime.
    """
    return value.strftime(fmt)


@experiments.app_template_filter("graph_to_img")
def graph_to_img_filter(graph):
    """Given a graph, return html to display it.
    """
    absolute_path = os.path.join(current_app.static_folder, "graphs/",
                                 graph.filename)
    if os.path.isfile(absolute_path):
        filename = graph.filename
    else:
        filename = current_app.config.get("EXPERIMENTS_PLACEHOLDER_GRAPH")

    graph_path = url_for('static', filename=os.path.join("graphs", filename))
    return Markup("<img src='" + graph_path + "'>")
