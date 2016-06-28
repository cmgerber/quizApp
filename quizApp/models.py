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
    """A User of the system.
    """

    name = db.Column(db.String(50))
    password = db.Column(db.String(50))
    authenticated = db.Column(db.Boolean)
    type = db.Column(db.String(50))

    __mapper_args__ = {
        'polymorphic_identity':'user',
        'polymorphic_on': type
    }

class Experimenter(User):
    """A User with permissions to modify Experiments.
    """

    __mapper_args__ = {
        'polymorphic_identity': 'experimenter',
    }

participant_dataset_table = Table(
    "participant_dataset", db.metadata,
    db.Column('participant_id', db.Integer, db.ForeignKey('participant.id')),
    db.Column('dataset_id', db.Integer, db.ForeignKey('dataset.id'))
)

class Participant(User):
    """A User that takes Experiments.

    Attributes:
        opt_in (bool): Has this user opted in to data collection?
        designed_datasets: Datasets this user has made visualizations for

    Relationships:
        M2M with Dataset
        O2M with Result
        O2M with ParticipantExperiment
        O2M with ParticipantQuestion
    """

    opt_in = db.Column(db.Boolean)

    designed_datasets = relationship("Dataset",
                                     secondary=participant_dataset_table)
    results = db.relationship("Result")
    experiments = db.relationship("ParticipantExperiment")
    questions = db.relationship("ParticipantQuestion")

participant_activity_table = Table(
    "participant_activity", db.metadata,
    db.Column("participant_id", db.Integer, db.ForeignKey('participant.id')),
    db.Column('activity_id', db.Integer, db.ForeignKey('experiment.id'))
)

class ParticipantExperiment(Base):
    """An Association Object that relates a User to an Experiment and also
    stores the progress of the User in this Experiment as well as the order of
    Questions that this user does.
    Essentially, this tracks the progress of each User in each Experiment.

    Attributes:
        activities - set: Order of activities for this user in this experiment
        progress - int: Which question the user is currently working on.

    Relationships:
        M2O with User
        M2O with Experiment
        M2M with Activity
    """

    progress = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    experiment_id = db.Column(db.Integer, db.ForeignKey('experiment.id'))
    activities = db.relationship("Activity",
                                 secondary=participant_activity_table)

activity_experiment_table = Table(
    "activity_experiment", db.metadata,
    db.Column("activity_id", db.Integer, db.ForeignKey('activity.id')),
    db.Column('experiment_id', db.Integer, db.ForeignKey('experiment.id'))

class Activity(Base):
    """An Activity is essentially a screen that a User sees while doing an
    Experiment. It may be an instructional screen or show a Question, or do
    something else.

    This class allows us to use Inheritance to easily have a variety of
    Activities in an Experiment, since we have a M2M between Experiment
    and Activity, while a specific Activity may actually be a Question thanks
    to SQLAlchemy's support for polymorphism.

    Attributes:
        activity_type - string: Discriminator column that determines what kind
        of Activity this is.

    Relationships:
        M2M with Experiment
    """

    activity_type = db.Column(db.String(20))
    experiments = db.relationship("Experiment",
                                  secondary=activity_experiment_table)






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
