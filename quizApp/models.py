from app import db

class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)


class Question(Base):
    __tablename__ = "questions"

    # id is combo of dataset number and question order
    dataset = db.Column(db.String)
    question = db.Column(db.String)
    #question, heuristic, rating, best_worst
    question_type = db.Column(db.String)
    answers = db.relationship("Answer")
    tests = db.relationship("StudentTest")

class Answer(Base):
    __tablename__ = "answers"

    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"))
    answer = db.Column(db.String)
    correct = db.Column(db.String) # TODO: should be bool

class Result(Base):
    __tablename__ = "results"
    # Result of student taking a StudentTest.
    # Many to one with student
    # Many to one with student_test TODO: how is this possible
    # Many to one with graph_id

    student_id = db.Column(db.Integer, db.ForeignKey("students.id"))
    student_test_id = db.Column(db.Integer, db.ForeignKey("students_test.id"))
    graph_id = db.Column(db.Integer, db.ForeignKey("graphs.id"))
    answer = db.Column(db.String)

class Student(Base):
    __tablename__ = "students"

    #progress: pre_test, training, post_test, complete
    progress = db.Column(db.String) #TODO: should be enum
    opt_in = db.Column(db.String)  #TODO: what is this?

    tests = db.relationship("StudentTest")

    results = db.relationship("Result")

class StudentTest(Base):
    # Each StudentTest ultimately associates a student, a graph, and a question.
    # many to one with student
    # many to one with graph
    # many to one with dataset
    # many to one with question
    __tablename__ = "students_test"

    student_id = db.Column(db.Integer, db.ForeignKey("students.id"))
    #pre_test, training, post_test
    test = db.Column(db.String) #TODO: enum

    graph_id = db.Column(db.Integer, db.ForeignKey('graphs.id'))
    graph = db.relationship("Graph")

    #ID of dataset of this question
    dataset = db.Column(db.Integer)

    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"))
    question = db.relationship("Question")

    order = db.Column(db.Integer) #TODO: what is this?
    complete = db.Column(db.String) #TODO: bool

    results = db.relationship("Result")

class Graph(Base):
    __tablename__ = "graphs"

    dataset = db.Column(db.Integer)
    graph_location = db.Column(db.String)
    results = db.relationship("Result")
