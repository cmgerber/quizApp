#!env/bin/python
# -*- coding: utf-8 -*-

from quizApp import app
import flask, uuid
from flask import request, url_for
from random import shuffle

from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import text, func, select, and_, or_, not_, desc, bindparam

from db_tables import metadata, Questions, Answers, Results, Students, StudentsTests, Graphs

#initialize db

def initializeDB():
    engine = create_engine('sqlite:///quizDB.db?check_same_thread=False', echo=True)
    conn = engine.connect()
    metadata.create_all(engine)
    return engine, conn

engine, conn = initializeDB()

#global variables
student_id_list = [1,2,3,4]

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

#quiz start button
@app.route('/_quizStart')
def quizStart():
    username, progress = conn.execute(select([Students.c.student_id, Students.c.progress]).\
                                            where(Students.c.student_id == flask.session['userid'])).fetchone()

    return flask.jsonify(progress=progress)

def get_question(order):
    progress, graph, questions, question_type answers, complete, dataset = conn.execute(select([Students.c.progress,
                                            StudentsTests.c.graph,
                                            Questions.c.question,
                                            Questions.c.question_type
                                            Answers.c.answer,
                                            StudentsTests.c.complete,
                                            StudentsTests.c.dataset]).\
                                select_from(StudentsTests.join(Students,
                                            Students.c.student_id == StudentsTests.c.student_id)).\
                                join(Questions,
                                     Questions.c.question_id == StudentsTests.c.question_id).\
                                join(Answers,
                                     Answers.c.question_id == Questions.c.question_id).\
                            where(and_(StudentsTests.c.student_id == flask.session['userid'],
                                  StudentsTests.c.test == Students.c.progress,
                                  StudentsTests.c.order == order))).fetchone()
    return progress, graph, questions, question_type answers, complete, dataset

#provide first quiz question
@app.route('/first_question')
def first_question():
    userid = flask.session['userid']

    params = request.args
    if 'o' in params:
        order = params['o']
    else:
        order = 1

    progress, graph, question, question_type, answers, complete, dataset = get_question(order)

    #check to make sure they have not done the question before
    if complete == 'yes':
        #this means the question has already been completed
        order_list = conn.execute(select([StudentsTests.c.order]).\
                             select_from(StudentsTests.join(Students,
                                         Students.c.student_id == StudentsTests.c.student_id)).\
                             where(and_(StudentsTests.c.student_id == flask.session['userid'],
                                   StudentsTests.c.complete == 'yes',
                                   StudentsTests.c.test == Student.c.progress))).fetchall()

        order_list = sorted(order_list, reverse=True)

        progress, graph, question, question_type, answers, complete, dataset = get_question(order_list[0]+1)


    #check which test
    if progress = 'pre_test':
        # query three graphs

        put in random order

        graph_list = conn.execute(select([Graphs.c.graph_location]).\
                                        where(Graphs.c.dataset == dataset)).fetchall()

        #randomly shuffle order of graphs
        suffle(graph_list)

        return graph_list, question, order

        # #use the 3 graphs for the current dataset based on order
        # graph_list = sorted(graph_list, key=lambda x: x[0])
        # if order > 4:
        #     return graph_list[:4], question
        # elif order > 3 and order < 7:
        #     return graph_list[4:7], question
        # else:
        #     return graph_list[7:], question
    elif progress == 'post_test':
        #three graphs and then survey
    elif progress == 'training':
        #multiple choice, one graph


