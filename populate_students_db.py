from sqlalchemy import create_engine
from sqlalchemy.sql import text, func, select, and_, or_, not_, desc, bindparam
from db_tables import metadata, Questions, Answers, Results, Students, StudentsTest, Graphs

import pandas as pd

engine = create_engine('sqlite:///quizDB.db?check_same_thread=False', echo=True)
conn = engine.connect()
metadata.create_all(engine)


df_questions = pd.read_excel('quizApp/data/question_table.xlsx', 'Sheet1')

#check for table and if it is there clear before writing to
if engine.dialect.has_table(engine.connect(), "questions"):
    conn.execute(Questions.delete())

conn.execute(Questions.insert(), [{'question_id':data.question_id,
                                  'dataset':data.dataset,
                                  'question':data.question,
                                  'question_type':data.question_type}
                                  for ix, data in df_questions.iterrows()])

df_answers = pd.read_excel('quizApp/data/answer_table.xlsx', 'Sheet1')

#check for table and if it is there clear before writing to
if engine.dialect.has_table(engine.connect(), "answers"):
    conn.execute(Answers.delete())


conn.execute(Answers.insert(), [{'answer_id':data.answer_id,
                                  'question_id':data.question_id,
                                  'answer':data.answer,
                                  'correct':data.correct}
                                  for ix, data in df_answers.iterrows()])


df_graphs = pd.read_excel('quizApp/data/graph_table.xlsx', 'Sheet1')


#check for table and if it is there clear before writing to
if engine.dialect.has_table(engine.connect(), "graphs"):
    conn.execute(Graphs.delete())


conn.execute(Graphs.insert(), [{'graph_id':data.graph_id,
                                  'dataset':data.dataset,
                                  'graph_location':data.graph_location}
                                  for ix, data in df_graphs.iterrows()])

#check for table and if it is there clear before writing to
if engine.dialect.has_table(engine.connect(), "students"):
    conn.execute(Students.delete())

conn.execute(Students.insert(), [{'student_id':sid,
                                  'progress':'pre_test',
                                  'opt_in':'na'}
                                  for sid in [x + 1 for x in range(60)]])


student_question_list = [[(1, 2), (3, 2), (4, 0), (2, 1), (5, 0), (0, 0)],
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
question_student_id_list = [x + 1 for x in range(30)]
heuristic_student_id_list = [x + 1 for x in range(30,60)]

def create_student_data(sid_list, test, group):
    for n, student in enumerate(student_question_list):
        student_id = sid_list[n]
        #count the order for each student per test
        order = 0
        for ix, graph in enumerate(student):
            student_test_id = int(str(student_id)+str(ix))
            dataset = graph[0]
            if dataset == 0:
                #not using 0 precursor for easier use in excel
                graph_id = graph[1]
            else:
                graph_id = int(str(dataset)+str(graph[1]))
            if test == 'pre_test' or test == 'post_test':
                order += 1
                if dataset == 0:
                    question_id = 6
                else:
                    question_id = int(str(dataset)+str(6))
                #write row to db
                conn.execute(StudentsTest.insert(), {'student_id':student_id,
                                    'test':test,
                                    'graph_id':graph_id,
                                    'dataset':dataset,
                                    'question_id':question_id,
                                    'order':order,
                                    'complete':'no'})
            elif group == 'heuristic':
                order += 1
                if dataset == 0:
                    question_id = 4
                else:
                    question_id = int(str(dataset)+str(4))
                #write row to db
                conn.execute(StudentsTest.insert(), {'student_id':student_id,
                                    'test':test,
                                    'graph_id':graph_id,
                                    'dataset':dataset,
                                    'question_id':question_id,
                                    'order':order,
                                    'complete':'no'})
            else:
                #multiple choice questions
                for x in range(3):
                    order += 1
                    if dataset == 0:
                        question_id = x + 1
                    else:
                        question_id = int(str(dataset)+str(x + 1))
                    #write row to db
                    conn.execute(StudentsTest.insert(), {'student_id':student_id,
                                    'test':test,
                                    'graph_id':graph_id,
                                    'dataset':dataset,
                                    'question_id':question_id,
                                    'order':order,
                                    'complete':'no'})
            order += 1
            if dataset == 0:
                question_id = 5
            else:
                question_id = int(str(dataset)+str(5))
            #write row to db
            conn.execute(StudentsTest.insert(), {'student_id':student_id,
                                'test':test,
                                'graph_id':graph_id,
                                'dataset':dataset,
                                'question_id':question_id,
                                'order':order,
                                'complete':'no'})

#check for table and if it is there clear before writing to
if engine.dialect.has_table(engine.connect(), "students_test"):
    conn.execute(StudentsTest.delete())

#create all the student_test table data
for test in ['pre_test', 'training', 'post_test']:
    create_student_data(question_student_id_list, test, 'question')
    create_student_data(heuristic_student_id_list, test, 'heuristic')





