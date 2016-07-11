"""Views that handle CRUD for experiments and rendering questions for
participants.
"""
import os
import json
from datetime import datetime
import pdb
from collections import defaultdict

from flask import Blueprint, render_template, url_for, Markup, jsonify, \
        abort, current_app
from flask_security import login_required, current_user, roles_required
from sqlalchemy import not_
from sqlalchemy.orm.exc import NoResultFound

from quizApp.models import Question, Choice, Experiment, \
        Assignment, ParticipantExperiment, Activity, Participant
from quizApp.forms.experiments import CreateExperimentForm, \
        DeleteExperimentForm, MultipleChoiceForm, ScaleForm, ActivityListForm
from quizApp import db

experiments = Blueprint("experiments", __name__, url_prefix="/experiments")


@experiments.route('', methods=["GET"])
@login_required
def read_experiments():
    """List experiments.
    """
    exps = Experiment.query.all()
    create_form = CreateExperimentForm()

    return render_template("experiments/read_experiments.html",
                           experiments=exps, create_form=create_form)


@experiments.route("", methods=["POST"])
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
    exp = Experiment.query.get(exp_id)

    if not exp:
        abort(404)

    try:
        part_exp = ParticipantExperiment.query.\
            filter_by(participant_id=current_user.id).\
            filter_by(experiment_id=exp_id).one()
    except NoResultFound:
        part_exp = None

    try:
        assignment = part_exp.assignments[part_exp.progress]
    except (IndexError, AttributeError):
        assignment = None

    update_experiment_form = CreateExperimentForm()

    return render_template("experiments/read_experiment.html", experiment=exp,
                           assignment=assignment,
                           update_experiment_form=update_experiment_form)


@experiments.route("/<int:exp_id>", methods=["DELETE"])
@roles_required("experimenter")
def delete_experiment(exp_id):
    """Delete an experiment.
    """
    pdb.set_trace()

    exp = Experiment.query.get(exp_id)

    if not exp:
        return jsonify({"success": 0})

    db.session.delete(exp)
    db.session.commit()

    return jsonify({"success": 1, "next_url":
                    url_for('experiments.read_experiments')})


@experiments.route("/<int:exp_id>/activities", methods=["PUT"])
@roles_required("experimenter")
def update_experiment_activities(exp_id):
    """Change what activities are contained in an experiment.
    """
    pdb.set_trace()
    try:
        exp = Experiment.query.get(exp_id)
    except NoResultFound:
        abort(404)

    activities_update_form = ActivityListForm()

    activities_pool = Activity.query.all()

    activities_mapping = activities_update_form.\
        populate_activities(activities_pool)

    if not activities_update_form.validate():
        abort(400)

    selected_activities = [int(a) for a in
                           activities_update_form.activities.data]

    for activity_id in selected_activities:
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
    experiment_update_form = CreateExperimentForm()

    if not experiment_update_form.validate():
        abort(400)

    try:
        exp = Experiment.query.get(exp_id)
    except NoResultFound:
        abort(404)

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
    assignment = Assignment.query.get(a_id)

    if not assignment:
        abort(404)

    activity = Activity.query.get(assignment.activity_id)

    if not activity:
        abort(404)

    if "question" in activity.type:
        return read_question(exp_id, activity)

    abort(404)


def get_question_form(question):
    """Given a question type, return the proper form.
    """
    if "scale" in question.type:
        return ScaleForm()
    else:
        return MultipleChoiceForm()


def read_question(exp_id, question):
    """Retrieve a question from the database and render its template.
    """
    experiment = Experiment.query.get(exp_id)
    participant = current_user
    assignment = Assignment.query.filter_by(participant_id=participant.id).\
        filter_by(activity_id=question.id).\
        filter_by(experiment_id=experiment.id).one()

    if assignment.choice_id:
        abort(400)

    if not experiment or not question:
        abort(404)

    question_form = get_question_form(question)
    question_form.populate_answers(question.choices)

    choice_order = [c.id for c in question.choices]
    assignment.choice_order = json.dumps(choice_order)
    assignment.save()

    return render_template("experiments/read_question.html", exp=experiment,
                           question=question, assignment=assignment,
                           mc_form=question_form)


@experiments.route('/<int:exp_id>/assignments/<int:a_id>', methods=["POST"])
def update_assignment(exp_id, a_id):
    """Record a user's answer to this assignment
    """
    assignment = Assignment.query.get(a_id)
    question = Question.query.get(assignment.activity_id)

    if not question:
        abort(404)

    if "question" not in assignment.activity.type:
        # Pass for now
        return jsonify({"success": 1})

    question_form = get_question_form(question)
    question_form.populate_answers(question.choices)

    if not question_form.validate():
        return jsonify({"success": 0})

    # User has answered this question successfully

    participant_id = current_user.id

    try:
        part_exp = ParticipantExperiment.query.\
                filter_by(experiment_id=exp_id).\
                filter_by(participant_id=participant_id).one()
    except NoResultFound:
        abort(404)

    # Get the user's assignment, associate it with the choice, and get the next
    # assignment
    assignment = part_exp.assignments[part_exp.progress]

    selected_choice = Choice.query.get(int(question_form.answers.data))

    if not selected_choice:
        # This choice does not exist
        abort(400)
    assignment.choice_id = selected_choice.id
    assignment.reflection = question_form.reflection.data
    part_exp.progress += 1

    try:
        next_assignment = part_exp.assignments[part_exp.progress]
    except IndexError:
        next_assignment = None
        part_exp.progress = -1

    if next_assignment:
        next_url = url_for("experiments.read_assignment", exp_id=exp_id,
                           a_id=part_exp.assignments[part_exp.progress].id)
    else:
        next_url = url_for("experiments.donedone")

    db.session.add(assignment)
    db.session.add(part_exp)
    db.session.commit()
    return jsonify({"success": 1, "explanation": question.explanation,
                    "next_url": next_url})


@experiments.route('/donedone')
@roles_required("participant")
def donedone():
    """Render a final done page.
    """
    return render_template('experiments/done.html')


@roles_required("participant")
@experiments.route('/done')
def done():
    """Collect some feedback before finalizing the experiment.
    """
    pass

    # questions = Question.query.join(StudentTest).\
    #         filter(StudentTest.student_id == flask.session['userid']).\
    #         all()

    # question_types = [q.question_type for q in questions]

    # if 'multiple_choice' in question_types:
    #     return render_template('experiments/doneA.html')
    # elif 'heuristic' in question_types:
    #     return render_template('experiments/doneB.html')
    # else:
    #     print "Unknown question types"


@experiments.route('/<int:exp_id>/settings', methods=["GET"])
@roles_required("experimenter")
def settings_experiment(exp_id):
    """Give information on an experiment and its activities.
    """
    experiment = Experiment.query.get(exp_id)

    if not experiment:
        abort(404)

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

    delete_experiment_form = DeleteExperimentForm()

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
    experiment = Experiment.query.get(exp_id)

    if not experiment:
        abort(404)

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
