#!env/bin/python
# -*- coding: utf-8 -*-

from quizApp import app
import flask, uuid
from flask import request, url_for
from random import shuffle
import os

from sqlalchemy.sql import text, func, select, and_, or_, not_, desc, bindparam
from sqlalchemy.orm.exc import NoResultFound

from models import Question, Answer, Result, Student, StudentsTest, Graph

# homepage
@app.route('/')
def home():
    return flask.render_template('index.html',
                                 is_home=True)

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
        student = Student.query.filter_by(id=userid).fetchone()
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
    questions = Question.query.join(StudenTest).\
            filter(StudentTest.student_id == flask.session['userid']).\
            all()

    question_types = [q.question_type for q in questions]

    """
    question_type = [x[0] for x in conn.execute(select([Questions.c.question_type]).\
            select_from(StudentsTest.join(Questions,
                 Questions.c.question_id == StudentsTest.c.question_id)).\
        where(StudentsTest.c.student_id == flask.session['userid'])).fetchall()]
    """

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
            add_columns(Student.progress,
                        Question.question,
                        Question.question_type,
                        Question.id).\
            filter(and_(
                StudentTest.student_id == flask.session["userid"],
                StudentTest.test == Student.progress,
                StudentTest.order == order)).\
            first()
    """
    progress, graph_id, questions, question_type, answers,\
            complete, dataset, student_test_id, \
            question_id = conn.execute(
                select([Students.c.progress,
                        StudentsTest.c.graph_id,
                        Questions.c.question,
                        Questions.c.question_type,
                        Answers.c.answer,
                        StudentsTest.c.complete,
                        StudentsTest.c.dataset,
                        StudentsTest.c.student_test_id,
                        Questions.c.question_id]).\
                select_from(StudentsTest.join(Students,
                                              Students.c.student_id == StudentsTest.c.student_id).\
                            join(Questions,
                                 Questions.c.question_id == StudentsTest.c.question_id)).\
                where(and_(StudentsTest.c.student_id == flask.session['userid'],
                           StudentsTest.c.test == Students.c.progress,
                           StudentsTest.c.order == order))).fetchone()
    """
    return test
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

    try:
        #progress, graph_id, question, question_type, answers, complete, dataset, student_test_id,question_id = get_question(order)
        test = get_question(order)
    except: #TODO: bad except
        complete = 'yes'
        progress = student.progress

    #check to make sure they have not done the question before
    if complete == 'yes':
        #this means the question has already been completed
        order_list = StudentTest.query.join(Student).\
                filter(and_(StudentTest.student_id == flask.session["userid"],
                            StudentTest.complete == "no",
                            StudentTest.test == Student.progress)).\
                all()
        """
        order_list = conn.execute(select([StudentsTest.c.order]).\
                             select_from(StudentsTest.join(Students,
                                         Students.c.student_id == StudentsTest.c.student_id)).\
                             where(and_(StudentsTest.c.student_id == flask.session['userid'],
                                   StudentsTest.c.complete == 'no',
                                   StudentsTest.c.test == Students.c.progress))).fetchall()
        """
        #TODO: how is this sorting?
        order_list = sorted(order_list)

        if len(order_list) >= 1:
            test = get_question(order_list[0].order)
        else:
            #the section has been completed, update progress and return to home page
            #update order back to start
            flask.session['order'] = 1
            progress_list = ['pre_test', 'training', 'post_test']
            ix = progress_list.index(progress) + 1
            if ix == len(progress_list):
                new_progress = 'complete'
            else:
                new_progress = progress_list[ix]
            student.progress = new_progress
            db.session.add(student)
            db.session.commit()
            #return to homepage
            if new_progress == 'complete':
                return flask.jsonify(progress='done')
            else:
                return flask.jsonify(progress='next')

    #put the student_test_id in session
    flask.session['student_test_id'] = test.id
    flask.session['order'] = test.order
    flask.session['question_type'] = test.question_type

    #check which test
    if progress == 'pre_test' or progress == 'post_test':
        # query three graphs
        graph_list = Graph.query.filter_by(dataset=dataset).all()
        """
        graph_list = conn.execute(select([Graphs.c.graph_location,
                                            Graphs.c.graph_id]).\
                                        where(Graphs.c.dataset == dataset)).fetchall()
        """
        #randomly shuffle order of graphs
        shuffle(graph_list)

        #put graph id's in session
        flask.session['graph1'] = graph_list[0][1]
        flask.session['graph2'] = graph_list[1][1]
        flask.session['graph3'] = graph_list[2][1]

        # TODO: can't we just pass the url
        return flask.jsonify(graph1='<img class=graph src=' + url_for('static',filename='graphs/'+str(graph_list[0][0])) + '>',
                             graph2='<img class=graph src=' + url_for('static',filename='graphs/'+str(graph_list[1][0])) + '>',
                             graph3='<img class=graph src=' + url_for('static',filename='graphs/'+str(graph_list[2][0])) + '>',
                             question=test.question,
                             question_type=test.question_type,
                             order=test.order,
                             progress=test.progress)

    elif progress == 'training':
        #get graph location
        graph = Graph.query.get(graph_id)
        """
        graph_location = conn.execute(select([Graphs.c.graph_location]).\
                                        where(Graphs.c.graph_id == graph_id)).fetchall()
        """
        #if it is a rating question just return graph
        if question_type == 'rating':
            flask.session['graph1'] = graph_id
            return flask.jsonify(graph1='<img class=graph src=' + url_for('static',filename='graphs/'+str(graph_location[0][0])) + '>',
                             question=question,
                             question_type=question_type,
                             order=order,
                             progress=progress)
        else:
            #get answers query
            answer_list = Answer.query.filter(question_id=question_id).all()
            """
            answer_list = conn.execute(select([Answers.c.answer,
                                              Answers.c.answer_id]).\
                                        where(Answers.c.question_id == question_id)).fetchall()
            """

            if question_type == 'heuristic':
                #put graph id's in session
                flask.session['graph1'] = graph_id
                flask.session['answer1'] = answer_list[0].answer
                flask.session['answer2'] = answer_list[1].answer
                flask.session['answer3'] = answer_list[2].answer
                flask.session['answer4'] = answer_list[3].answer
                flask.session['answer5'] = answer_list[4].answer

                return flask.jsonify(graph1='<img src=' + url_for('static',filename='graphs/'+str(graph_location[0][0])) + ' height="500" width="500">',
                                     question=question,
                                     question_type=question_type,
                                     order=order,
                                     progress=progress,
                                     answer1=answer_list[0][0],
                                     answer2=answer_list[1][0],
                                     answer3=answer_list[2][0],
                                     answer4=answer_list[3][0],
                                     answer5=answer_list[4][0])
                #TODO: can we just return an array of answers?
            else:
                #put graph id's in session
                #TODO: factor out
                flask.session['graph1'] = graph_id
                flask.session['answer1'] = answer_list[0].answer
                flask.session['answer2'] = answer_list[1].answer
                flask.session['answer3'] = answer_list[2].answer

                return flask.jsonify(graph1='<img src=' + url_for('static',filename='graphs/'+str(graph_location[0][0])) + ' height="500" width="500">',
                                     question=question,
                                     question_type=question_type,
                                     order=order,
                                     progress=progress,
                                     answer1=answer_list[0].answer,
                                     answer2=answer_list[1].answer,
                                     answer3=answer_list[2].answer)


#get answers to question, write to db then get next question
@app.route('/_pretest_answers')
def pretest_answers():
    params = request.args

    #update order number
    flask.session['order'] = flask.session['order'] + 1

    #data
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
    except:
        answer_list = [(best1,graph1),(best2,graph2),(best3,graph3)]

    #write to db
    #update complete row in StudentsTest table
    test = StudentTest.query.get(student_test_id)
    test.complete = "yes"
    db.session.add(test)
    db.session.commit()
    """
    r = conn.execute(StudentsTest.update().\
                     where(StudentsTest.c.student_test_id == student_test_id).\
                     values(complete='yes'))
"""
    for answer in answer_list:
        result = Result(
            student_id=student_id,
            student_test_id=student_test_id,
            answer=answer[0],
            graph_id=answer[1])
        session.add(result)

    session.commit()
    """
    conn.execute(Results.insert(), [{
                      'student_id':student_id,
                      'student_test_id':student_test_id,
                      'answer':answer[0],
                      'graph_id':answer[1],
                      } for answer in answer_list])
    """
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
    """
    conn.execute(Results.insert(), [{
                      'student_id':student_id,
                      'student_test_id':int(str(student_id) + str(answer[1])),
                      'answer':answer[0],
                      'graph_id':'na',
                      } for answer in answer_list])
    """

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
    db.session.add(student_test)

    for answer in answer_list:
        result = Result(
            student_id=student_id,
            student_test_id=student_test_id,
            answer=answer[0],
            graph_id=answer[1])
        db.session.add(result)
    db.session.commit()


    """
    r = conn.execute(StudentsTest.update().\
            where(StudentsTest.c.student_test_id == student_test_id).\
            values(complete='yes'))

    conn.execute(Results.insert(), [{
    'student_id':student_id,
    'student_test_id':student_test_id,
    'answer':answer[0],
    'graph_id':answer[1],
    } for answer in answer_list])
    """
    #get next question
    # question_json = first_question()
    # return question_json
    return flask.jsonify(result={"status": 200})
