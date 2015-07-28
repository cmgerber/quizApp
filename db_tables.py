from sqlalchemy import MetaData, Table, Column, BigInteger, Date, Float, Integer, Text, String, DateTime, ForeignKey

metadata = MetaData()

Questions = Table('questions', metadata,
    # combo of dataset number and question order
    Column('question_id', Integer, primary_key = True),
    Column('dataset', String),
    Column('question', String),
    #question, heuristic, rating, best_worst
    Column('question_type', String),
)

Answers = Table('answers', metadata,
    Column('answer_id', Integer, primary_key = True),
    Column('question_id', Integer, ForeignKey('questions.question_id')),
    #list of answer options for question
    Column('answer', String),
    #yes or no
    Column('correct', String),
)

Results = Table('results', metadata,
    Column('results_id', Integer, primary_key = True),
    Column('student_id', Integer, ForeignKey('students.student_id')),
    Column('student_test_id', Integer, ForeignKey('students_test.student_test_id')),
    Column('answer', String),
    Column('correct', String),
)

Students = Table('students', metadata,
    Column('student_id', Integer, primary_key = True),
    #progress: pre_test, training, post_test, complete
    Column('progress', String),
    Column('opt_in', String),
    )

StudentsTest = Table('students_test', metadata,
    #one row for each question per student
    Column('student_test_id', Integer, primary_key = True),
    Column('student_id', Integer, ForeignKey('students.student_id')),
    #pre_test, training, post_test
    Column('test', String),
    #combo of dataset and graph num
    Column('graph_id', Integer, ForeignKey('graphs.graph_id')),
    Column('dataset', Integer),
    # combo of dataset number and question order
    Column('question_id', Integer, ForeignKey('questions.question_id')),
    Column('order', Integer),
    #yes or no, for checking progress
    Column('complete', String),
    )

Graphs = Table('graphs', metadata,
    Column('graph_id', Integer, primary_key = True),
    Column('dataset', Integer),
    Column('graph_location', String),
    )


