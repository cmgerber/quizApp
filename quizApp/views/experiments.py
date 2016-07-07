from flask import Blueprint, render_template, url_for, Markup, jsonify, abort
from quizApp.models import Question, Choice, Participant, Graph, Experiment, \
        User, Assignment, ParticipantExperiment, Activity
from quizApp.forms.experiments import CreateExperimentForm, \
        DeleteExperimentForm, MultipleChoiceForm, ScaleForm
from flask_security import login_required, current_user, roles_required
from sqlalchemy.orm.exc import NoResultFound
import os
from quizApp import db
import json
import pdb

experiments = Blueprint("experiments", __name__, url_prefix="/experiments")

@experiments.route('/', methods=["GET"])
@login_required
def read_experiments():
    """List experiments.
    """
    exps = Experiment.query.all()
    create_form = CreateExperimentForm()
    delete_form = DeleteExperimentForm()

    return render_template("experiments/read_experiments.html",
                           experiments=exps, create_form=create_form,
                           delete_form=delete_form)

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
        abort(400)

    try:
        assignment = part_exp.assignments[part_exp.progress]
    except IndexError:
        assignment = None

    return render_template("experiments/read_experiment.html", experiment=exp,
                          assignment=assignment)

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

@experiments.route("/<int:exp_id>", methods=["PUT"])
@roles_required("experimenter")
def update_experiment():
    """Modify an experiment's properties.
    """
    try:
        name = request.args["name"]
        start = request.args["start"]
        stop = request.args["stop"]
    except KeyError:
        return 000;

    try:
        exp = Experiment.query.filter_by(name=name).one()
    except NoResultFoiund:
        return 000

    if name:
        exp.name = name
    if start:
        exp.start = start
    if stop:
        exp.stop = stop

    exp.save()

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

@experiments.route("/<int:exp_id>/modification_form")
@roles_required("experimenter")
def experiment_modification_form_html(exp_id):
    """Get an HTML representation of a modification form for the given
    experiment.

    I'm not really happy with this, but I can't think of another method that
    minimizes repitition of code. I am open to suggestions...
    """
    exp = Experiment.query.get(exp_id)
    modify_form = CreateExperimentForm()

    if not exp:
        abort(404)

    return render_template("experiments/experiment_modification_form.html", exp=exp,
                   modify_form=modify_form)

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
    graph_path = url_for('static', filename=os.path.join("graphs/",
                                                         graph.filename))

    return Markup("<img src='" + graph_path + "' \>")
