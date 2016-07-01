"""Models for the quizApp.
"""

from quizApp import db
from enum import Enum

class Base(db.Model):
    """All models have an identical id field.
    """
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    def save(self, commit=True):
        """Save this model to the database.

        If commit is True, then the session will be comitted as well.
        """
        db.session.add(self)

        if commit:
            db.session.commit()

class User(Base):
    """A User is used for authentication.

    Each User may be associated with a Student, in this case the User is
    considered to have the permissions of a Student.

    Otherwise, the User is considered to be an admin.

    Students log in using their ID's and do not have passwords. For students,
    the user's name is their ID. For others, they log in using their name
    and their password.

    Relationships:

    OtO with Student
    """

    name = db.Column(db.String(50))
    password = db.Column(db.String(50))
    authenticated = db.Column(db.Boolean, default=False)

    def is_active(self):
        """All users are active, so return True"""
        return True

    def get_id(self):
        return unicode(self.id)

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False

class Experiment(Base):
    """An experiment contains a set of Questions.

    name: The name of this experiment.
    created: A datetime representing when this experiment was created.
    start: A datetime representing when this experiment begins accepting
        responses.
    stop: A datetime representing when this experiment stops accepting
        responses.

    Relationships:

    OtM wth Question
    OtM with Graph
    """

    #TODO: how do we associate graphs here? Should graphs be a part of
    # question? For now we will not create the relationships.
    name = db.Column(db.String(150), index=True)
    created = db.Column(db.DateTime)
    start = db.Column(db.DateTime)
    stop = db.Column(db.DateTime)

class Question(Base):
    """A Question appears on a StudentTest and has an Answer.

    Relationships:
        MtO with dataset
        OtM with answers
        MtO with StudentTest

    dataset: The dataset this Question belongs to
    question: A string representation of this question
    question_type: e.g. heuristic or question
    answers: all answers that this question has
    tests: all tests including this question
    """
    __tablename__ = "questions"

    # id is combo of dataset number and question order

    dataset = db.Column(db.String(10))
    question = db.Column(db.String(200))
    #question, heuristic, rating, best_worst
    question_type = db.Column(db.String(50))

    answers = db.relationship("Answer")
    tests = db.relationship("StudentTest")

class Answer(Base):
    """An answer is a possible answer to a question.

    Relationships:
        MtO with Question

    answer: The answer to this question, as a string
    correct: True if this is the correct answer to the question
    """
    __tablename__ = "answers"

    answer = db.Column(db.String(200))
    correct = db.Column(db.String(5)) # TODO: should be bool

    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"))

class Result(Base):
    #TODO: how does this class work
    __tablename__ = "results"
    # Result of student taking a StudentTest.
    # Many to one with student
    # Many to one with student_test TODO: how is this possible
    # Many to one with graph_id

    student_id = db.Column(db.Integer, db.ForeignKey("students.id"))
    student_test_id = db.Column(db.Integer, db.ForeignKey("students_test.id"))
    graph_id = db.Column(db.Integer, db.ForeignKey("graphs.id"))
    answer = db.Column(db.String(200))

class Progress(Enum):
    pre_test = 0
    training = 1
    post_test = 2

class Student(Base):
    """A Student.

    progress: how far the student has gotten in the quiz
    opt_in: if the student has opted in to data collection

    Relationships:
        OtM with StudentTest
        OtM with Result
    """
    __tablename__ = "students"

    #progress: pre_test, training, post_test, complete
    progress = db.Column(db.String(50))
    opt_in = db.Column(db.String(10))

    tests = db.relationship("StudentTest")
    results = db.relationship("Result")

class StudentTest(Base):
    """Each StudentTest ultimately associates a student, a graph, and a
        question.

    Relationships:
        MtO with Student
        MtO with graph
        MtO with dataset
        MtO with question

    test: e.g. pretest, training, posttest
    order: order of this test for display
    complete: if this test is complete
    """
    __tablename__ = "students_test"

    student_id = db.Column(db.Integer, db.ForeignKey("students.id"))
    #pre_test, training, post_test
    test = db.Column(db.String(50)) #TODO: enum

    dataset = db.Column(db.Integer)
    order = db.Column(db.Integer) #TODO: what is this?
    complete = db.Column(db.String(5)) #TODO: bool

    graph_id = db.Column(db.Integer, db.ForeignKey('graphs.id'))
    graph = db.relationship("Graph")

    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"))
    question = db.relationship("Question")

    results = db.relationship("Result")

class Graph(Base):
    """A graph is a visualization of a dataset.

    graph_location: Path to this graph
    Relationships:
        MtO with dataset
        OtM with StudentTest
        OtM with Result
    """
    __tablename__ = "graphs"

    dataset = db.Column(db.Integer)
    graph_location = db.Column(db.String(100))

    results = db.relationship("Result")
