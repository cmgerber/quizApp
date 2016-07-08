"""Models for the quizApp.
"""

from quizApp import db
from flask_security import UserMixin, RoleMixin


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

roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(),
                                 db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(),
                                 db.ForeignKey('role.id')))


class Role(Base, RoleMixin):
    """A Role describes what a User can and can't do.
    """
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(Base, UserMixin):
    """A User is used for authentication.

    Attributes:
        name: string: The username of this user.
        password: string: This user's password.
        authenticated: bool: True if this user is authenticated.
        type: string: The type of this user, e.g. experimenter, participant
    """

    email = db.Column(db.String(255), unique=True)
    active = db.Column(db.Boolean())
    password = db.Column(db.String(255))
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship("Role", secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    type = db.Column(db.String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': type
    }


participant_dataset_table = db.Table(
    "participant_dataset", db.metadata,
    db.Column('participant_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('dataset_id', db.Integer, db.ForeignKey('dataset.id'))
)


class Participant(User):
    """A User that takes Experiments.

    Attributes:
        opt_in (bool): Has this user opted in to data collection?
        designed_datasets: Datasets this user has made visualizations for

    Relationships:
        M2M with Dataset
        O2M with Assignment (parent)
        O2M with ParticipantExperiment (parent)
    """

    opt_in = db.Column(db.Boolean)

    designed_datasets = db.relationship("Dataset",
                                        secondary=participant_dataset_table)
    assignments = db.relationship("Assignment")
    experiments = db.relationship("ParticipantExperiment")

    __mapper_args__ = {
        'polymorphic_identity': 'participant',
    }


class ParticipantExperiment(Base):
    """An Association Object that relates a User to an Experiment and also
    stores the progress of the User in this Experiment as well as the order of
    Questions that this user does.
    Essentially, this tracks the progress of each User in each Experiment.

    Attributes:
        activities - set: Order of activities for this user in this experiment
        progress - int: Which question the user is currently working on.

    Relationships:
        M2O with Participant (child)
        M2O with Experiment (child)
        O2M with Assignment (parent)
    """

    progress = db.Column(db.Integer)

    participant_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    experiment_id = db.Column(db.Integer, db.ForeignKey('experiment.id'))
    assignments = db.relationship("Assignment")


assignment_graph_table = db.Table(
    "assignment_graph", db.metadata,
    db.Column("assignment_id", db.Integer,
              db.ForeignKey("assignment.id")),
    db.Column("graph_id", db.Integer, db.ForeignKey("graph.id"))
)


class Assignment(Base):
    """For a given Activity, determine which Graphs, if any, a particular
    Participant sees, as well as recording the Participant's answer, or if
    they skipped this assignment.

    Attributes:
        skipped - bool: True if the Participant skipped this Question, False
                         otherwise
        reflection - string: A reflection on why this participant answered this
            question in this way.
        choice_order - string: A JSON object in string form that represents the
            order of choices that this participant was presented with when
            answering this question, e.g. {[1, 50, 9, 3]} where the numbers are
            the IDs of those choices.

    Relationships:
        M2M with Graph
        M2O with Participant (child)
        M2O with Activity (child)
        M2O with Choice (specifically, which answer this User chose) (child)
        M2O with Experiment (child)
        M2O with ParticipantExperiment (child)
    """

    skipped = db.Column(db.Boolean)
    reflection = db.Column(db.String(200))
    choice_order = db.Column(db.String(80))

    graphs = db.relationship("Graph", secondary=assignment_graph_table)
    participant_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    activity_id = db.Column(db.Integer, db.ForeignKey("activity.id"))
    choice_id = db.Column(db.Integer, db.ForeignKey("choice.id"))
    experiment_id = db.Column(db.Integer, db.ForeignKey("experiment.id"))
    participant_experiment_id = db.Column(
        db.Integer,
        db.ForeignKey("participant_experiment.id"))


activity_experiment_table = db.Table(
    "activity_experiment", db.metadata,
    db.Column("activity_id", db.Integer, db.ForeignKey('activity.id')),
    db.Column('experiment_id', db.Integer, db.ForeignKey('experiment.id'))
)


class Activity(Base):
    """An Activity is essentially a screen that a User sees while doing an
    Experiment. It may be an instructional screen or show a Question, or do
    something else.

    This class allows us to use Inheritance to easily have a variety of
    Activities in an Experiment, since we have a M2M between Experiment
    and Activity, while a specific Activity may actually be a Question thanks
    to SQLAlchemy's support for polymorphism.

    Attributes:
        type - string: Discriminator column that determines what kind
        of Activity this is.

    Relationships:
        M2M with Experiment
        O2M with Assignment (parent)
    """

    type = db.Column(db.String(50))
    experiments = db.relationship("Experiment",
                                  secondary=activity_experiment_table)
    assignments = db.relationship("Assignment")

    __mapper_args__ = {
        'polymorphic_identity': 'activity',
        'polymorphic_on': type
    }

question_dataset_table = db.Table(
    "question_dataset", db.metadata,
    db.Column("question_id", db.Integer, db.ForeignKey("activity.id")),
    db.Column("dataset_id", db.Integer, db.ForeignKey("dataset.id"))
)


class Question(Activity):
    """A Question is related to one or more Graphs and has one or more Choices,
    and is a part of one or more Experiments.

    Attributes:
        question - string: This question as a string
        explantion - string: The explanation for why the correct answer is
            correct.
        needs_reflection - bool: True if the participant should be asked why
            they picked what they did after they answer the question.
        duration - int: If nonzero, how long (in milliseconds) to display the
            graphs before hiding them again.

    Relationships:
       O2M with Choice (parent)
       M2M with Dataset - if empty, this Question is universal
    """

    question = db.Column(db.String(200))
    choices = db.relationship("Choice")
    datasets = db.relationship("Dataset", secondary=question_dataset_table)
    explanation = db.Column(db.String(200))
    needs_reflection = db.Column(db.Boolean())
    duration = db.Column(db.Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'question',
    }


class MultipleChoiceQuestion(Question):
    """A MultipleChoiceQuestion has one or more choices that are correct.
    """
    __mapper_args__ = {
        'polymorphic_identity': 'question_mc',
    }


class SingleSelectQuestion(MultipleChoiceQuestion):
    """A SingleSelectQuestion allows only one Choice to be selected.
    """

    __mapper_args__ = {
        'polymorphic_identity': 'question_mc_singleselect',
    }


class MultiSelectQuestion(MultipleChoiceQuestion):
    """A MultiSelectQuestion allows any number of Choices to be selected.
    """

    __mapper_args__ = {
        'polymorphic_identity': 'question_mc_multiselect',
    }


class ScaleQuestion(SingleSelectQuestion):
    """A ScaleQuestion is like a SingleSelectQuestion, but it displays
    its options horizontally. This is useful for "strongly agree/disagree"
    sort of questions.
    """

    __mapper_args__ = {
        'polymorphic_identity': 'question_mc_singleselect_scale',
    }


class FreeAnswerQuestion(Question):
    """A FreeAnswerQuestion allows a Participant to enter an arbitrary answer.
    """

    __mapper_args__ = {
        'polymorphic_identity': 'question_freeanswer',
    }


class Choice(Base):
    """ A Choice is a string that is a possible answer for a Question.

    Attributes:
        choice - string: The choice as a string.
        label - string: The label for this choice (1,2,3,a,b,c etc)
        correct - bool: "True" if this choice is correct, "False" otherwise

    Relationships:
        M2O with Question (child)
        O2M with Assignment (parent)
    """
    choice = db.Column(db.String(200))
    label = db.Column(db.String(3))
    correct = db.Column(db.Boolean)

    question_id = db.Column(db.Integer, db.ForeignKey("activity.id"))
    assignments = db.relationship("Assignment")


class Graph(Base):
    """A Graph is an image file located on the server that may be shown in
    conjunction with a Question.

    Attributes:
        filename - string: Filename of the graph

    Relationships:
        M2M with Assignment
        M2O with Dataset (child)
    """

    filename = db.Column(db.String(100))
    assignments = db.relationship(
        "Assignment",
        secondary=assignment_graph_table)
    dataset_id = db.Column(db.Integer, db.ForeignKey("dataset.id"))


class Experiment(Base):
    """An Experiment contains a list of Activities.

    Attributes:
      name - string
      created - datetime
      start - datetime: When this experiment becomes accessible for answers
      stop - datetime: When this experiment stops accepting answers

    Relationships:
      M2M with Activity
      O2M with ParticipantExperiment (parent)
      O2M with Assignment (parent)
    """

    name = db.Column(db.String(150), index=True)
    created = db.Column(db.DateTime)
    start = db.Column(db.DateTime)
    stop = db.Column(db.DateTime)

    activities = db.relationship("Activity",
                                 secondary=activity_experiment_table)
    participant_experiments = db.relationship("ParticipantExperiment")
    assignment = db.relationship("Assignment")


class Dataset(Base):
    """A Dataset represents some data that graphs are based on.

    Attributes:
        name - string
        uri - A path or descriptor of where this dataset is located.

    Relationships:
        O2M with Graph (parent)
        M2M with Question
        M2M with Participant
    """
    name = db.Column(db.String(100))
    uri = db.Column(db.String(200))

    graphs = db.relationship("Graph")
    questions = db.relationship("Question", secondary=question_dataset_table)
    participant = db.relationship("Participant",
                                  secondary=participant_dataset_table)
