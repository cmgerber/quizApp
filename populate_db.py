#!/bin/env python2

from quizApp.models import Question, Answer, Result, Student, StudentTest, \
        Graph, Experiment
from quizApp import db
from sqlalchemy import and_
import pandas as pd
from datetime import datetime, timedelta
import os

db.drop_all()
db.create_all()

exp1 = Experiment(name="experiment1",
                 start=datetime.now(),
                 stop=datetime.now() + timedelta(days=3))

exp2 = Experiment(name="experiment2",
                 start=datetime.now() + timedelta(days=-3),
                 stop=datetime.now())

db.session.add(exp1)
db.session.add(exp2)

DATA_ROOT = "quizApp/data/"

questions = pd.read_excel(os.path.join(DATA_ROOT,
                                       'DatasetsAndQuestions.xlsx'),
                          'Questions')

for _, data in questions.iterrows():
    question = Question(
        id = data.question_id,
        dataset = data.dataset_id,
        question = data.question_text,
        question_type=data.question_type)
    db.session.add(question)

answers = pd.read_excel(os.path.join(DATA_ROOT, 'DatasetsAndQuestions.xlsx'),
                          'Answers')
for _, data in answers.iterrows():
    answer = Answer(
        id=data.answer_id,
        question_id=data.question_id,
        answer=data.answer_text,
        correct=data.correct)
    db.session.add(answer)

df_graphs = pd.read_excel(os.path.join(DATA_ROOT, 'graph_table.xlsx'),
                          'Sheet1')

for _, data in df_graphs.iterrows():
    graph = Graph(
            id=data.graph_id,
            dataset=data.dataset,
            graph_location=data.graph_location)
    db.session.add(graph)


# In this list, each list is associated with a student (one to one).
# The first three tuples in each list are associated with training questions.
# The last three tuples in each list are associated with pre/post questions.
# In each tuple, the first number represents the dataset of the question.
# The second number is associated with the ID of the graph. TODO: simplify this
#   relationship.
# The order of the tuples along with the student id gives the student test id.
# Note: No student has two tuples with the same dataset - this means the
#   relationship between student test and dataset is many to one.

student_question_list = \
[[(1, 2), (3, 2), (4, 0), (2, 1), (5, 0), (0, 0)],
 [(1, 2), (0, 2), (5, 1), (2, 0), (3, 0), (4, 1)],
 [(3, 0), (2, 1), (4, 0), (5, 1), (0, 0), (1, 2)],
 [(5, 2), (2, 2), (0, 1), (1, 0), (3, 1), (4, 0)],
 [(2, 2), (0, 1), (3, 1), (4, 0), (1, 1), (5, 1)],
 [(0, 0), (3, 0), (1, 0), (2, 2), (5, 2), (4, 2)],
 [(4, 2), (1, 1), (5, 2), (0, 0), (3, 1), (2, 1)],
 [(4, 2), (3, 0), (1, 2), (0, 1), (5, 2), (2, 1)],
 [(3, 1), (2, 0), (4, 2), (1, 1), (0, 1), (5, 2)],
 [(0, 2), (4, 1), (3, 0), (5, 0), (1, 1), (2, 0)],
 [(5, 1), (4, 1), (0, 2), (3, 2), (1, 2), (2, 0)],
 [(2, 1), (5, 0), (0, 2), (3, 2), (4, 2), (1, 1)],
 [(3, 1), (5, 2), (4, 1), (0, 2), (2, 0), (1, 0)],
 [(1, 1), (5, 1), (2, 2), (4, 0), (3, 1), (0, 2)],
 [(2, 0), (1, 0), (5, 0), (4, 1), (0, 2), (3, 2)],
 [(1, 1), (5, 1), (0, 2), (4, 2), (2, 1), (3, 1)],
 [(5, 1), (4, 2), (2, 0), (1, 2), (3, 2), (0, 1)],
 [(0, 0), (2, 2), (1, 0), (4, 1), (5, 2), (3, 2)],
 [(0, 1), (1, 2), (5, 2), (2, 0), (4, 2), (3, 0)],
 [(1, 0), (3, 2), (0, 0), (2, 2), (4, 0), (5, 0)],
 [(3, 2), (2, 1), (4, 1), (1, 0), (5, 1), (0, 0)],
 [(1, 0), (3, 2), (5, 0), (0, 1), (4, 1), (2, 2)],
 [(5, 2), (3, 1), (1, 1), (0, 0), (4, 0), (2, 2)],
 [(4, 1), (0, 0), (3, 1), (2, 1), (5, 1), (1, 0)],
 [(5, 0), (2, 0), (0, 1), (3, 0), (1, 1), (4, 2)],
 [(0, 2), (4, 0), (1, 1), (3, 1), (2, 2), (5, 0)],
 [(2, 0), (0, 0), (3, 0), (1, 2), (5, 0), (4, 1)],
 [(0, 1), (4, 2), (2, 1), (5, 2), (1, 0), (3, 0)],
 [(5, 0), (4, 0), (2, 2), (3, 0), (1, 2), (0, 1)],
 [(4, 0), (1, 2), (2, 1), (5, 1), (0, 2), (3, 2)]]

#temp created student id list
# question_student_id_list = [x + 1 for x in range(30)]
# heuristic_student_id_list = [x + 1 for x in range(30,60)]

#read in student lists
df_sid = pd.read_csv(os.path.join(DATA_ROOT, 'student_id_list.csv'))
df_sid.Questions = df_sid.Questions.apply(lambda x: int(x))
df_sid.Heuristics = df_sid.Heuristics.apply(lambda x: int(x))
question_student_id_list = [int(x) for x in list(df_sid.Questions)]
heuristic_student_id_list = [int(x) for x in list(df_sid.Heuristics)]
combined_id_list = question_student_id_list + heuristic_student_id_list

for sid in combined_id_list:
    student = Student(
            id=sid,
            progress='pre_test', #TODO: enum
            opt_in='na', #TODO: enum
            )
    db.session.add(student)

db.session.commit()

def create_student_data(sid_list, student_question_list, test, group):
    """
    sid_list: list of student id's
    student_question_list: magic list of lists of tuples
    test: pre_test or training or post_test
    group: question or heuristic
    """
    missing_qs = set()
    if test == 'pre_test' or test == 'post_test':
        question_list = [x[:3] for x in student_question_list]
    else:
        #pick last three
        question_list = [x[3:] for x in student_question_list]
    for n, student in enumerate(question_list):
        #n is the nth student
        student_id = sid_list[n]
        #count the order for each student per test
        order = 0
        for ix, graph in enumerate(student):
            student_test_id = int(str(student_id)+str(ix))
            dataset = graph[0]
            graph_id = int(str(dataset)+str(graph[1]+1))

            if test == 'pre_test' or test == 'post_test':
                order += 1
                #TODO: why +5
                question_id = int(str(dataset)+str(5))

                if not Question.query.get(question_id):
                    missing_qs.add(question_id)
                    continue

                #write row to db
                student_test = StudentTest(
                        student_id=student_id,
                        test=test,
                        graph_id=graph_id,
                        dataset=dataset,
                        question_id=question_id,
                        order=order,
                        complete="no")

                db.session.add(student_test)

            else: #training
                if group == 'heuristic':
                    #three questions per dataset, three datasets, so 9 questions
                    # for the training part
                    for x in range(6,9):
                        order += 1
                        question_id = int(str(dataset)+str(x))

                        if not Question.query.get(question_id):
                            missing_qs.add(question_id)
                            continue

                        #write row to db
                        student_test = StudentTest(
                                student_id=student_id,
                                test=test,
                                graph_id=graph_id,
                                dataset=dataset,
                                question_id=question_id,
                                order=order,
                                complete="no")

                        db.session.add(student_test)
                else:
                    #multiple choice questions
                    for x in range(3):
                        order += 1
                        question_id = int(str(dataset)+str(x + 1))
                        #write row to db
                        if not Question.query.get(question_id):
                            missing_qs.add(question_id)
                            continue
                        student_test = StudentTest(
                                student_id=student_id,
                                test=test,
                                graph_id=graph_id,
                                dataset=dataset,
                                question_id=question_id,
                                order=order,
                                complete="no")

                        db.session.add(student_test)

                #only have rating question for training
                order += 1
                question_id = int(str(dataset)+str(4))
                #write row to db
                if not Question.query.get(question_id):
                    missing_qs.add(question_id)
                    continue

                student_test = StudentTest(
                        student_id=student_id,
                        test=test,
                        graph_id=graph_id,
                        dataset=dataset,
                        question_id=question_id,
                        order=order,
                        complete="no")

                db.session.add(student_test)

    db.session.commit()
    print "Completed storing {} {} tests".format(test, group)
    print "Failed to find the following questions:"
    print missing_qs

#create all the student_test table data
for test in ['pre_test', 'training', 'post_test']:
    create_student_data(question_student_id_list, student_question_list, test, 'question')
    create_student_data(heuristic_student_id_list, student_question_list, test, 'heuristic')


#Verify

for sid in question_student_id_list + heuristic_student_id_list:
    for progress in ["pre_test", "training", "post_test"]:
        tests = StudentTest.query.join(Student).\
                filter(and_(StudentTest.student_id == sid,
                            StudentTest.test == progress)).all()
        order = set()
        for test in tests:
            if test.order in order:
                pdb.set_trace()
            order.add(test.order)
