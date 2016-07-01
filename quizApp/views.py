from datetime import datetime
from random import shuffle
import os
import pdb
import uuid

import flask
from flask import render_template, request, url_for, abort
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import text, func, select, and_, or_, not_, desc, bindparam
from flask_login import login_required, logout_user, login_user, current_user

from quizApp import app, db, login_manager
from quizApp import csrf
from quizApp import forms
from quizApp.models import Question, Choice, Participant, Graph, Experiment, \
        User, Assignment, ParticipantExperiment, Activity

# homepage
@app.route('/')
def home():
    return flask.render_template('index.html',
                                 is_home=True)

@login_manager.user_loader
def user_loader(user_id):
    """Load the given user id.
    """
    return User.query.get(int(user_id))

@app.route('/experiments', methods=["GET"])
@login_required
def read_experiments():
    """List experiments.
    """
    exps = Experiment.query.all()
    create_form = forms.CreateExperimentForm()
    delete_form = forms.DeleteExperimentForm()

    return render_template("experiments.html", experiments=exps,
                          create_form=create_form, delete_form=delete_form)

@app.route('/experiments/<int:exp_id>', methods=["GET"])
@login_required
def read_experiment(exp_id):
    """View the landing page of an experiment, along with the ability to start.
    """
    exp = Experiment.query.get(exp_id)

    if not exp:
        abort(404)

    try:
        part_exp = ParticipantExperiment.query.\
                filter_by(participant_id=flask.session["userid"]).\
                filter_by(experiment_id=exp_id).one()
    except NoResultFound:
        abort(400)

    try:
        activity = Activity.query.get(
            part_exp.assignments[part_exp.progress].activity_id)
    except IndexError:
        activity = None

    return render_template("read_experiment.html", experiment=exp,
                          activity=activity)

@app.route("/experiments", methods=["POST"])
@login_required
def create_experiment():
    """Create an experiment and save it to the database.
    """
    form = forms.CreateExperimentForm()
    if not form.validate_on_submit():
        abort(400)

    exp = Experiment(
        name=form.name.data,
        start=form.start.data,
        stop=form.stop.data,
        created=datetime.now())

    exp.save()

    return render_template("create_experiment_response.html", exp=exp,
                           delete_form=forms.DeleteExperimentForm())

@app.route("/experiments/<int:exp_id>", methods=["DELETE"])
@login_required
def delete_experiment(exp_id):
    """Delete an experiment.
    """
    form = forms.DeleteExperimentForm()
    #TODO: auth

    if not form.validate():
        return flask.jsonify({"success": 0})

    exp = Experiment.query.get(exp_id)

    if not exp:
        return flask.jsonify({"success": 0})

    db.session.delete(exp)
    db.session.commit()

    return flask.jsonify({"success": 1, "id": request.json["id"]})

@app.route("/experiments/<int:exp_id>", methods=["PUT"])
@login_required
def update_experiment():
    """Modify an experiment's properties.

    Arguments should be None unless they should be updated.
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

@app.route('/experiments/<int:exp_id>/questions/<int:q_id>')
@login_required
def read_question(exp_id, q_id):
    experiment = Experiment.query.get(exp_id)
    question = Question.query.get(q_id)
    participant = Participant.query.get(flask.session["userid"])
    assignment = Assignment.query.filter_by(participant_id=participant.id).\
            filter_by(activity_id=question.id).\
            filter_by(experiment_id=experiment.id).one()

    if assignment.choice_id:
        abort(400)

    pdb.set_trace()

    if not experiment or not question:
        abort(404)

    if "scale" in question.type:
        question_form = forms.ScaleForm()
    else:
        question_form = forms.MultipleChoiceForm()

    question_form.answers.choices = [(str(c.id), c.choice) for c in
                               question.choices]

    return render_template("show_question.html", exp=experiment,
                           question=question, assignment=assignment,
                           mc_form=question_form)

@app.route('/experiments/<int:exp_id>/questions/<int:q_id>', methods=["POST"])
def update_question(exp_id, q_id):
    """Record a user's answer to this question
    """
    pdb.set_trace()

    question = Question.query.get(q_id)

    if not question:
        abort(404)

    #TODO: factor this code out
    if "scale" in question.type:
        question_form = forms.ScaleForm()
    else:
        question_form = forms.MultipleChoiceForm()
    question_form.answers.choices = [(str(c.id), c.choice) for c in
                               question.choices]

    if not question_form.validate():
        return flask.jsonify({"success": 0})

    # User has answered this question successfully

    participant_id = flask.session["userid"]

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

    part_exp.progress += 1

    try:
        next_assignment = part_exp.assignments[part_exp.progress]
    except IndexError:
        next_assignment = None

    if next_assignment:
        next_url = url_for("read_question", exp_id=exp_id,
                           q_id=part_exp.assignments[part_exp.progress].\
                           activity_id)
    else:
        next_url = url_for("donedone")

    db.session.add(assignment)
    db.session.add(part_exp)
    db.session.commit()
    return flask.jsonify({"success": 1, "next_url": next_url})

@app.route("/experiments/<int:exp_id>/modification_form")
@login_required
def experiment_modification_form_html(exp_id):
    """Get an HTML representation of a modification form for the given
    experiment.

    I'm not really happy with this, but I can't think of another method that
    minimizes repitition of code. I am open to suggestions...
    """
    exp = Experiment.query.get(exp_id)
    modify_form = forms.CreateExperimentForm()

    if not exp:
        abort(404)

    return render_template("experiment_modification_form.html", exp=exp,
                   modify_form=modify_form)

@app.route('/login', methods=["GET", "POST"])
def login():
    pdb.set_trace()
    form = forms.LoginForm()

    if form.validate_on_submit():
       user = User.query.get(int(form.name.data))
       if user:
           login_user(user)
           flask.flash("Logged in successfully.")
           return flask.redirect(flask.url_for("home"))

    return render_template("login.html", form=form)

@app.route("/logout", methods=["GET"])
@login_required
def logout():
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return flask.redirect(flask.url_for("home"))

#TODO: done vs donedone

#Complete page
@app.route('/donedone')
def donedone():
    return flask.render_template('done.html')

#Complete page
@app.route('/done')
def done():
    questions = Question.query.join(StudentTest).\
            filter(StudentTest.student_id == flask.session['userid']).\
            all()

    question_types = [q.question_type for q in questions]

    #TODO: enum
    if 'multiple_choice' in question_types:
        return flask.render_template('doneA.html')
    elif 'heuristic' in question_types:
        return flask.render_template('doneB.html')
    else:
        #TODO: proper logging
        print "Unknown question types"
