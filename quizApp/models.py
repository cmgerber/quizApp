from sqlalchemy import MetaData, Table, Column, BigInteger, Date, Float, Integer, Text, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

class Base(object):
    id = Column(Integer, primary_key=True)


Base = declarative_base()

metadata = MetaData()

class Question(Base):
    __tablename__ = "questions"

    # id is combo of dataset number and question order
    dataset = Column(String)
    question = Column(String)
    #question, heuristic, rating, best_worst
    question_type = Column(String)
    answers = relationship("Answer")

class Answer(Base):
    __tablename__ = "answers"

    question_id = Column(Integer, ForeignKey("questions.id"))
    answer = Column(String)
    correct = Column(String) # TODO: should be bool

class Result(Base):
    __tablename__ = "results"

    student =

Results = Table('results', metadata,
    Column('results_id', Integer, primary_key = True),
    Column('student_id', Integer, ForeignKey('students.student_id')),
    Column('student_test_id', Integer, ForeignKey('students_test.student_test_id')),
    Column('answer', String),
    Column('graph_id', Integer, ForeignKey('graphs.graph_id'))
)

class Student(Base):
    __tablename__ = "students"

    #progress: pre_test, training, post_test, complete
    progress = Column(String) #TODO: should be enum
    opt_in = Column(String)  #TODO: what is this?

    tests = relationship("StudentTests")

class StudentTest(Base):
    __tablename__ = "students_test"

    student_id = Column(Integer, ForeignKey("students.id")
    #pre_test, training, post_test
    test = Column(String) #TODO: enum

    graph_id = Column(Integer, ForeignKey('graph.id'))
    graph = relationship("Graph")

    dataset = Column(Integer) #TODO: what does this represent?


StudentsTest = Table('students_test', metadata,
    #one row for each question per student
    Column('student_test_id', Integer, primary_key = True),
    Column('student_id', Integer, ForeignKey('students.student_id')),
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

class Graph(Base):
    __tablename__ = "graphs"



Graphs = Table('graphs', metadata,
    Column('graph_id', Integer, primary_key = True),
    Column('dataset', Integer),
    Column('graph_location', String),
    )
