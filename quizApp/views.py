from datetime import datetime
from random import shuffle
import os
import pdb
import uuid

import flask
from flask import render_template, request, url_for, abort
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import text, func, select, and_, or_, not_, desc, bindparam

from quizApp import app,db
from quizApp import csrf
from quizApp import forms
from quizApp.models import Question, Answer, Result, Student, StudentTest, \
        Graph, Experiment

# homepage
@app.route('/')
def home():
    return flask.render_template('index.html',
                                 is_home=True)
@app.route('/experiments')
def read_experiments():
    """List experiments.
    """
    exps = Experiment.query.all()
    create_form = forms.CreateExperimentForm()
    delete_form = forms.DeleteExperimentForm()

    return render_template("experiments.html", experiments=exps,
                          create_form=create_form, delete_form=delete_form)

@app.route('/experiments/<int:exp_id>')
def view_experiment(exp_id):
    """View the landing page of an experiment, along with the ability to start.
    """
    exp = Experiment.query.get(exp_id)

    if not exp:
        abort(404)

    return render_template("view_experiment.html", experiment=exp)

@app.route("/experiments/create", methods=["POST"])
def create_experiment():
    """Create an experiment and save it to the database.
    """
    form = forms.CreateExperimentForm()
    if not form.validate_on_submit():
        return flask.jsonify({"success": 0})

    exp = Experiment(
        name=form.name.data,
        start=form.start.data,
        stop=form.stop.data,
        created=datetime.now())

    exp.save()

    return flask.jsonify({"success": 1})

@app.route("/experiments/delete", methods=["POST"])
def delete_experiment():
    """Delete an experiment.
    """
    form = forms.DeleteExperimentForm()
    #TODO: auth

    pdb.set_trace()

    if not form.validate_on_submit():
        return flask.jsonify({"success": 0})

    exp = Experiment.query.get(request.json["id"])

    if not exp:
        return flask.jsonify({"success": 0})

    db.session.delete(exp)
    db.session.commit()

    return flask.jsonify({"success": 1, "id": request.json["id"]})

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

@app.route('/_login')
def login():
    #TODO: careful casting to int
    #TODO: we should just use flask-login
    username = int(request.args['username'])

    try:
        user = Student.query.filter_by(id=username).one()
    except NoResultFound:
        return flask.jsonify(result='bad')

    flask.session['userid'] = username
    return flask.jsonify(result='ok',
                         username=username)

@app.route('/_logout')
def logout():
    flask.session.pop('userid', None)
    return flask.jsonify(result='ok')

@app.route('/_check_login')
def check_login():
    userid = flask.session['userid'] if 'userid' in flask.session else None
    if userid:
        student = Student.query.filter_by(id=userid).one()
        username = student.id
        progress = student.progress
    else:
        username = None
        progress = None
    return flask.jsonify(logged_in='userid' in flask.session,
                         username=username,
                         progress=progress)

@app.route('/_clear_session')
def clear_session():
    thisuser = None
    if 'userid' in flask.session:
        thisuser = flask.session['userid']
    flask.session.clear()
    if thisuser:
        flask.session['userid'] = thisuser

    return flask.jsonify(done=True)

#pretest
@app.route('/pre_test')
def pre_test():
    return flask.render_template('pretest.html')

#posttest
@app.route('/post_test')
def post_test():
    return flask.render_template('posttest.html')

#training
@app.route('/training')
def training():
    return flask.render_template('training.html')

#landing page between tests
@app.route('/next')
def next():
    return flask.render_template('lobby.html')

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

#quiz start button
@app.route('/_quizStart')
def quizStart():
    student = Student.query.filter_by(id=flask.session["userid"]).one()

    return flask.jsonify(progress=student.progress)

def get_question(order):
    test = StudentTest.query.\
            join(Student).\
            join(Question).\
            add_columns(Student.progress, #TODO: do we need all these columns
                        Question.question,
                        Question.question_type,
                        StudentTest.complete,
                        StudentTest.dataset,
                        Question.id.label("question_id")).\
            filter(and_(
                StudentTest.student_id == flask.session["userid"],
                StudentTest.test == Student.progress,
                StudentTest.order == order))

    return test.first()
    #return progress, graph_id, questions, question_type, answers, complete, dataset, student_test_id, question_id

#provide first quiz question
@app.route('/first_question')
def first_question():
    userid = flask.session['userid']
    student = Student.query.get(flask.session["userid"])

    try:
        order = flask.session['order']
    except: #TODO: bad except
        order = 1

    #progress, graph_id, question, question_type, answers, complete, dataset, student_test_id,question_id = get_question(order)
    test = get_question(order)
    if test:
        complete = test.complete
        progress = test.progress
    else:
        complete = 'yes'
        progress = student.progress

    #check to make sure they have not done the question before
    if complete == 'yes':
        #this means the question has already been completed
        #TODO: maybe just sort by order on the query?
        order_list = StudentTest.query.join(Student).\
                filter(and_(StudentTest.student_id == flask.session["userid"],
                            StudentTest.complete == "no",
                            StudentTest.test == Student.progress)).\
                    all()
        order_list = sorted(order_list, key=lambda x: x.order)

        if len(order_list) >= 1:
            #TODO: log error, this should not happen...
            test = get_question(order_list[0].order)
        else:
            #the section has been completed, update progress and return to home page
            #update order back to start
            #TODO: what does order mean?
            flask.session['order'] = 1
            #TODO: enum
            progress_list = ['pre_test', 'training', 'post_test']

            try:
                student.progress = progress_list[progress_list.index(progress) + 1]
            except IndexError:
                student.progress = "complete"

            db.session.commit()
            #return to homepage
            if student.progress == 'complete':
                return flask.jsonify(progress='done')
            else:
                return flask.jsonify(progress='next')

    #put the student_test_id in session
    flask.session['student_test_id'] = test[0].id
    flask.session['order'] = test[0].order
    flask.session['question_type'] = test.question_type

    #check which test
    if test.progress == 'pre_test' or test.progress == 'post_test':
        # query three graphs
        graph_list = Graph.query.filter_by(dataset=test.dataset).all()
        #randomly shuffle order of graphs
        shuffle(graph_list)

        #put graph id's in session
        flask.session['graph1'] = graph_list[0].id
        flask.session['graph2'] = graph_list[1].id
        flask.session['graph3'] = graph_list[2].id

        # Find urls of each graph
        graph_urls = [url_for('static',
            filename='graphs/'+str(graph.graph_location)) for graph in graph_list]

        return flask.jsonify(
                             graphs=graph_urls,
                             question=test.question,
                             question_type=test.question_type,
                             order=test[0].order,
                             progress=test.progress)

    elif progress == 'training':
        pdb.set_trace()
        graph_id = test[0].graph_id
        #get graph location
        graph = Graph.query.get(graph_id)
        graph_urls = [url_for('static',
            filename='graphs/' + graph.graph_location)]
        flask.session['graph1'] = graph_id
        #if it is a rating question just return graph
        if test.question_type == 'rating':
            return flask.jsonify(graphs=graph_urls,
                             question=test.question,
                             question_type=test.question_type,
                             order=test.order,
                             progress=test.progress)
        else:
            #get answers query
            answer_list = Answer.query.filter_by(question_id=test.question_id).all()
            answer_strings = [a.answer for a in answer_list]

            for i, answer in enumerate(answer_strings):
                #TODO: zero index
                flask.session['answer' + str(i + 1)] = answer

            if test.question_type == 'heuristic':
                #put graph id's in session

                return flask.jsonify(graphs=graph_urls,
                                     question=test.question,
                                     question_type=test.question_type,
                                     order=test[0].order,
                                     progress=test.progress,
                                     answers=answer_strings)

            else:
                #put graph id's in session
                return flask.jsonify(graphs=graph_urls,
                                     question=test.question,
                                     question_type=test.question_type,
                                     order=test[0].order,
                                     progress=test.progress,
                                     answers=answer_strings)

#get answers to question, write to db then get next question
@app.route('/_pretest_answers')
def pretest_answers():
    params = request.args

    #update order number
    flask.session['order'] = flask.session['order'] + 1

    #data
    #TODO: would it make sense to just grab best* and graph*?
    best1 = params['best1']
    best2 = params['best2']
    best3 = params['best3']
    order = params['order']
    graph1 = flask.session['graph1']
    graph2 = flask.session['graph2']
    graph3 = flask.session['graph3']
    student_test_id = flask.session['student_test_id']
    student_id = flask.session['userid']

    try:
        best4 = params['best4']
        answer_list = [(best1,graph1),(best2,graph2),(best3,graph3),(best4,'na')]
    except KeyError:
        answer_list = [(best1,graph1),(best2,graph2),(best3,graph3)]

    #write to db
    #update complete row in StudentsTest table
    test = StudentTest.query.get(student_test_id)
    test.complete = "yes"
    db.session.commit()
    for answer in answer_list:
        result = Result(
            student_id=student_id,
            student_test_id=student_test_id,
            answer=answer[0],
            graph_id=answer[1])
        db.session.add(result)

    db.session.commit()
    #get next question
    # question_json = first_question()
    # return question_json
    return flask.jsonify(result={"status": 200})

#get answers to question, write to db then get next question
@app.route('/_posttest_answers')
def posttest_answers():
    params = request.args

    #update order number
    flask.session['order'] = flask.session['order'] + 1

    #data
    best1 = params['best1']
    best2 = params['best2']
    order = params['order']
    #student_test_id = flask.session['student_test_id']
    student_id = flask.session['userid']


    answer_list = [(best1,1000), (best2,1001)]

    #write to db
    #update complete row in StudentsTest table
    # r = conn.execute(StudentsTest.update().\
    #                  where(StudentsTest.c.student_test_id == student_test_id).\
    #                  values(complete='yes'))

    for answer in answer_list:
        result = Result(
            student_id=student_id,
            student_test_id=int(str(student_id) + str(answer[1])),
            answer=answer[0],
            graph_id="na"
        )

    #get next question
    # question_json = first_question()
    # return question_json
    return flask.jsonify(result={"status": 200})

#get answers to question, write to db then get next question
@app.route('/_training_answers')
def training_answers():
    params = request.args

    #update order number
    flask.session['order'] = flask.session['order'] + 1

    #data
    order = params['order']
    graph1 = flask.session['graph1']
    student_test_id = flask.session['student_test_id']
    student_id = flask.session['userid']

    #TODO: not very well thought out
    if flask.session['question_type'] == 'rating':
        answer_id = params['rating1']
    else:
        answer1 = params['best1']
        #figure out answer
        if answer1 == 'optionA':
            answer_id = flask.session['answer1']
        elif answer1 == 'optionB':
            answer_id = flask.session['answer2']
        elif answer1 == 'optionC':
            answer_id = flask.session['answer3']
        elif answer1 == 'optionD':
            answer_id = flask.session['answer4']
        elif answer1 == 'optionE':
            answer_id = flask.session['answer5']


    answer_list = [(answer_id,graph1)]

    #write to db
    #update complete row in StudentsTest table
    student_test = StudentTest.query.get(student_test_id)
    student_test.complete = "yes"

    for answer in answer_list:
        result = Result(
            student_id=student_id,
            student_test_id=student_test_id,
            answer=answer[0],
            graph_id=answer[1])
        db.session.add(result)
    db.session.commit()

    #get next question
    # question_json = first_question()
    # return question_json
    return flask.jsonify(result={"status": 200})
