from flask import Blueprint, render_template, url_for, Markup, jsonify, \
        abort, current_app
from quizApp.models import Question, Choice, Participant, Graph, Experiment, \
        User, Assignment, ParticipantExperiment, Activity
from quizApp.forms.experiments import CreateExperimentForm, \
        DeleteExperimentForm, MultipleChoiceForm, ScaleForm, ActivityListForm
from flask_security import login_required, current_user, roles_required
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import not_
import os
from quizApp import db
from quizApp.config import basedir
import json
from datetime import datetime

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

    return render_template("experiments/create_experiment_response.html", exp=exp,
                           delete_form=DeleteExperimentForm())

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
    form = DeleteExperimentForm()

    if not form.validate():
        return jsonify({"success": 0})

    exp = Experiment.query.get(exp_id)

    if not exp:
        return jsonify({"success": 0})

    db.session.delete(exp)
    db.session.commit()

    return jsonify({"success": 1, "id": request.json["id"]})

@experiments.route("/<int:exp_id>/activities", methods=["PUT"])
@roles_required("experimenter")
def update_experiment_activities(exp_id):
    """Change what activities are contained in an experiment.
    """
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
        activity = Activity.query.get(activity_id)
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
    assignment = Assignment.query.get(a_id)

    if not assignment:
        abort(404)

    activity = Activity.query.get(assignment.activity_id)

    if not activity:
        abort(404)

    if "question" in activity.type:
        return read_question(exp_id, activity)

    abort(404)

def read_question(exp_id, question):
    experiment = Experiment.query.get(exp_id)
    participant = current_user
    assignment = Assignment.query.filter_by(participant_id=participant.id).\
            filter_by(activity_id=question.id).\
            filter_by(experiment_id=experiment.id).one()

    if assignment.choice_id:
        abort(400)

    if not experiment or not question:
        abort(404)

    if "scale" in question.type:
        question_form = ScaleForm()
    else:
        question_form = MultipleChoiceForm()

    question_form.answers.choices = [(str(c.id), c.choice) for c in
                               question.choices]

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

    #TODO: factor this code out
    if "scale" in question.type:
        question_form = ScaleForm()
    else:
        question_form = MultipleChoiceForm()
    question_form.answers.choices = [(str(c.id), c.choice) for c in
                               question.choices]

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

    #TODO: sqlalchemy validators
    assignment.choice_id = selected_choice.id
    assignment.reflection = question_form.reflection.data
    part_exp.progress += 1

    try:
        next_assignment = part_exp.assignments[part_exp.progress]
    except IndexError:
        next_assignment = None

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

#TODO: done vs donedone

#Complete page
@experiments.route('/donedone')
@roles_required("participant")
def donedone():
    return render_template('experiments/done.html')

#Complete page
@roles_required("participant")
@experiments.route('/done')
def done():
    questions = Question.query.join(StudentTest).\
            filter(StudentTest.student_id == flask.session['userid']).\
            all()

    question_types = [q.question_type for q in questions]

    #TODO: enum
    if 'multiple_choice' in question_types:
        return render_template('experiments/doneA.html')
    elif 'heuristic' in question_types:
        return render_template('experiments/doneB.html')
    else:
        #TODO: proper logging
        print "Unknown question types"


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
    return Markup("<img src='" + graph_path + "' \>")

@experiments.route('/<int:exp_id>/settings', methods=["GET"])
@roles_required("experimenter")
def settings_experiment(exp_id):
    """Give information on an experiment and its activities.
    """
    experiment = Experiment.query.get(exp_id)

    if not experiment:
        abort(404)

    update_experiment_form = CreateExperimentForm()
    remove_activities_form = ActivityListForm(prefix="remove")
    add_activities_form = ActivityListForm(prefix="add")

    remove_activities_mapping = remove_activities_form.populate_activities(
        experiment.activities)

    add_activities_mapping = add_activities_form.populate_activities(
        Activity.query.\
            filter(not_(Activity.experiments.any(id=experiment.id))).all())
    return render_template("experiments/settings_experiment.html",
                           experiment=experiment,
                           update_experiment_form=update_experiment_form,
                           remove_activities_form=remove_activities_form,
                           add_activities_form=add_activities_form,
                           add_activities_mapping=add_activities_mapping,
                           remove_activities_mapping=remove_activities_mapping)
