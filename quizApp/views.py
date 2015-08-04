#!env/bin/python
# -*- coding: utf-8 -*-

from quizApp import app
import flask, uuid
from flask import request, url_for
from random import shuffle
import os

from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import text, func, select, and_, or_, not_, desc, bindparam

from db_tables import metadata, Questions, Answers, Results, Students, StudentsTest, Graphs

#initialize db

def initializeDB():
    #project_root = '/projects/oev/quizApp_Project/'
    project_root = os.path.dirname(os.path.realpath('quizApp_Project/'))
    DATABASE = os.path.join(project_root, 'quizDB.db')
    engine = create_engine('sqlite:///{0}?check_same_thread=False'.format(DATABASE), echo=True)
    conn = engine.connect()
    metadata.create_all(engine)
    return engine, conn

engine, conn = initializeDB()

#global variables
student_id_list = [x+1 for x in range(60)]

app.secret_key = str(uuid.uuid4())

# homepage
@app.route('/')
def home():
    return flask.render_template('index.html',
                                 is_home=True)

@app.route('/_login')
def login():
    #flask.session.clear()
    username = int(request.args['username'])

    if username in student_id_list:
        flask.session['userid'] = username
        return flask.jsonify(result='ok',
                             username=username)
    else:
        return flask.jsonify(result='bad')

@app.route('/_logout')
def logout():
    #flask.session.clear()
    flask.session.pop('userid',None)
    return flask.jsonify(result='ok')

@app.route('/_check_login')
def check_login():
    userid = flask.session['userid'] if 'userid' in flask.session else None
    if 'userid' in flask.session:
        username, progress = conn.execute(select([Students.c.student_id, Students.c.progress]).\
                                            where(Students.c.student_id == flask.session['userid'])).fetchone()
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
    return flask.render_template('pretest.html')

#training
@app.route('/training')
def training():
    return flask.render_template('training.html')

#landing page between tests
@app.route('/next')
def next():
    return flask.render_template('lobby.html')

#Complete page
@app.route('/done')
def done():
    return flask.render_template('done.html')

#quiz start button
@app.route('/_quizStart')
def quizStart():
    username, progress = conn.execute(select([Students.c.student_id, Students.c.progress]).\
                                            where(Students.c.student_id == flask.session['userid'])).fetchone()

    return flask.jsonify(progress=progress)

def get_question(order):
    progress, graph_id, questions, question_type, answers, complete, dataset, student_test_id, question_id = conn.execute(select([Students.c.progress,
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
    return progress, graph_id, questions, question_type, answers, complete, dataset, student_test_id, question_id

#provide first quiz question
@app.route('/first_question')
def first_question():
    userid = flask.session['userid']

    try:
        order = flask.session['order']
    except:
        order = 1

    try:
        progress, graph_id, question, question_type, answers, complete, dataset, student_test_id,question_id = get_question(order)
    except:
        complete = 'yes'
        progress = conn.execute(select([Students.c.progress]).\
                                where(Students.c.student_id == flask.session['userid'])).fetchone()
        progress = progress[0]

    #check to make sure they have not done the question before
    if complete == 'yes':
        #this means the question has already been completed
        order_list = conn.execute(select([StudentsTest.c.order]).\
                             select_from(StudentsTest.join(Students,
                                         Students.c.student_id == StudentsTest.c.student_id)).\
                             where(and_(StudentsTest.c.student_id == flask.session['userid'],
                                   StudentsTest.c.complete == 'no',
                                   StudentsTest.c.test == Students.c.progress))).fetchall()

        order_list = sorted(order_list)

        if len(order_list) >= 1:
            progress, graph_id, question, question_type, answers, complete, dataset, student_test_id, question_id = get_question(order_list[0][0])
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
            r = conn.execute(Students.update().\
                             where(Students.c.student_id == flask.session['userid']).\
                             values(progress=new_progress))
            #return to homepage
            if new_progress == 'complete':
                return flask.jsonify(progress='done')
            else:
                return flask.jsonify(progress='next')

    #put the student_test_id in session
    flask.session['student_test_id'] = student_test_id
    flask.session['order'] = order
    flask.session['question_type'] = question_type

    #check which test
    if progress == 'pre_test':
        # query three graphs

        graph_list = conn.execute(select([Graphs.c.graph_location,
                                            Graphs.c.graph_id]).\
                                        where(Graphs.c.dataset == dataset)).fetchall()

        #randomly shuffle order of graphs
        shuffle(graph_list)

        #put graph id's in session
        flask.session['graph1'] = graph_list[0][1]
        flask.session['graph2'] = graph_list[1][1]
        flask.session['graph3'] = graph_list[2][1]


        return flask.jsonify(graph1='<img src=' + url_for('static',filename='graphs/'+str(graph_list[0][0])) + ' height="500" width="500">',
                             graph2='<img src=' + url_for('static',filename='graphs/'+str(graph_list[1][0])) + ' height="500" width="500">',
                             graph3='<img src=' + url_for('static',filename='graphs/'+str(graph_list[2][0])) + ' height="500" width="500">',
                             question=question,
                             question_type=question_type,
                             order=order,
                             progress=progress)

    elif progress == 'post_test':
        filler = 1
        #three graphs and then survey
    elif progress == 'training':
        #get graph location
        graph_location = conn.execute(select([Graphs.c.graph_location]).\
                                        where(Graphs.c.graph_id == graph_id)).fetchall()

        #if it is a rating question jsut return graph
        if question_type == 'rating':
            flask.session['graph1'] = graph_id
            return flask.jsonify(graph1='<img src=' + url_for('static',filename='graphs/'+str(graph_location[0][0])) + ' height="500" width="500">',
                             question=question,
                             question_type=question_type,
                             order=order,
                             progress=progress)
        else:
            #get answers query
            answer_list = conn.execute(select([Answers.c.answer,
                                              Answers.c.answer_id]).\
                                        where(Answers.c.question_id == question_id)).fetchall()

            try:
                answer_list[0][1]
            except:
                if len(answer_list) >1:
                    longg
                elif len(answer_list) <= 1:
                    shortt

            #put graph id's in session
            flask.session['graph1'] = graph_id
            flask.session['answer1'] = answer_list[0][1]
            flask.session['answer2'] = answer_list[1][1]
            flask.session['answer3'] = answer_list[2][1]

            return flask.jsonify(graph1='<img src=' + url_for('static',filename='graphs/'+str(graph_location[0][0])) + ' height="500" width="500">',
                                 question=question,
                                 question_type=question_type,
                                 order=order,
                                 progress=progress,
                                 answer1=answer_list[0][0],
                                 answer2=answer_list[1][0],
                                 answer3=answer_list[2][0])
            #multiple choice, one graph

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


    answer_list = [(best1,graph1),(best2,graph2),(best3,graph3)]

    #write to db
    #update complete row in StudentsTest table
    r = conn.execute(StudentsTest.update().\
                     where(StudentsTest.c.student_test_id == student_test_id).\
                     values(complete='yes'))

    conn.execute(Results.insert(), [{
                      'student_id':student_id,
                      'student_test_id':student_test_id,
                      'answer':answer[0],
                      'graph_id':answer[1],
                      } for answer in answer_list])

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


    answer_list = [(answer_id,graph1)]

    #write to db
    #update complete row in StudentsTest table
    r = conn.execute(StudentsTest.update().\
                     where(StudentsTest.c.student_test_id == student_test_id).\
                     values(complete='yes'))

    conn.execute(Results.insert(), [{
                      'student_id':student_id,
                      'student_test_id':student_test_id,
                      'answer':answer[0],
                      'graph_id':answer[1],
                      } for answer in answer_list])

    #get next question
    # question_json = first_question()
    # return question_json
    return flask.jsonify(result={"status": 200})


#keep track of multiple choice question answer clicks
# @app.route('/_answer_tracking')
# def answer_tracking():
#     params = request.args

#     #put currently selected answer in session
#     answer1 = params['answer1']
#     if answer1 == 'optionA':
#         answer_id = flask.session['answer1']
#     elif answer1 == 'optionB':
#         answer_id = flask.session['answer2']
#     elif answer1 == 'optionC':
#         answer_id = flask.session['answer3']
#     flask.session['answer_id'] = answer_id

#     return flask.jsonify(result={"status": 200})
