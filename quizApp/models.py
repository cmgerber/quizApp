"""Models for the quizApp.
"""
import os

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
    password = db.Column(db.String(255), nullable=False)
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship("Role", secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    type = db.Column(db.String(50), nullable=False)

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
    assignments = db.relationship("Assignment", backref="participant")
    experiments = db.relationship("ParticipantExperiment",
                                  backref="participant")

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
        complete - bool: True if the user has finalized their responses, False
            otherwise

    Relationships:
        M2O with Participant (child)
        M2O with Experiment (child)
        O2M with Assignment (parent)
    """

    progress = db.Column(db.Integer, nullable=False, default=0)
    complete = db.Column(db.Boolean, default=False)

    participant_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    experiment_id = db.Column(db.Integer, db.ForeignKey('experiment.id'))

    assignments = db.relationship("Assignment",
                                  backref="participant_experiment")

    @db.validates('assignments')
    def validate_assignments(self, _, assignment):
        """The Assignments in this model must be related to the same Experiment
        as this model is."""
        assert assignment.experiment_id == self.experiment_id
        assert assignment.participant_id == self.participant_id
        assert assignment.activity in self.experiment.activities
        return assignment


assignment_media_item_table = db.Table(
    "assignment_media_item", db.metadata,
    db.Column("assignment_id", db.Integer,
              db.ForeignKey("assignment.id")),
    db.Column("media_item_id", db.Integer, db.ForeignKey("media_item.id"))
)


class Assignment(Base):
    """For a given Activity, determine which MediaItems, if any, a particular
    Participant sees, as well as recording the Participant's answer, or if
    they skipped this assignment.

    Attributes:
        skipped - bool: True if the Participant skipped this Question, False
                         otherwise
        comment - string: An optional comment entered by the student.
        choice_order - string: A JSON object in string form that represents the
            order of choices that this participant was presented with when
            answering this question, e.g. {[1, 50, 9, 3]} where the numbers are
            the IDs of those choices.

    Relationships:
        M2M with MediaItem
        M2O with Participant (child)
        M2O with Activity (child)
        M2O with Choice (specifically, which answer this User chose) (child)
        M2O with ParticipantExperiment (child)
    """

    skipped = db.Column(db.Boolean)
    comment = db.Column(db.String(200))
    choice_order = db.Column(db.String(80))

    media_items = db.relationship("MediaItem",
                                  secondary=assignment_media_item_table)
    participant_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    activity_id = db.Column(db.Integer, db.ForeignKey("activity.id"))
    activity = db.relationship("Activity", back_populates="assignments")

    choice_id = db.Column(db.Integer, db.ForeignKey("choice.id"))
    experiment_id = db.Column(db.Integer, db.ForeignKey("experiment.id"))
    participant_experiment_id = db.Column(
        db.Integer,
        db.ForeignKey("participant_experiment.id"))

    @db.validates("activity")
    def validate_activity(self, _, activity):
        """Make sure that the activity is part of this experiment.
        """
        assert self.experiment in activity.experiments
        return activity

    @db.validates("choice_id")
    def validate_choice_id(self, _, choice_id):
        """This must be a valid choice, i.e. contained in the question (if any)
        """
        if "question" in self.activity.type:
            assert(choice_id in [c.id for c in self.activity.choices])

        return choice_id


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
        category - string: A description of this assignment's category, for the
            users' convenience.

    Relationships:
        M2M with Experiment
        O2M with Assignment (parent)
    """

    type = db.Column(db.String(50), nullable=False)
    experiments = db.relationship("Experiment",
                                  secondary=activity_experiment_table)
    assignments = db.relationship("Assignment", back_populates="activity",
                                  cascade="all")
    category = db.Column(db.String(100))

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
    """A Question is related to one or more MediaItems and has one or more Choices,
    and is a part of one or more Experiments.

    Attributes:
        question - string: This question as a string
        explantion - string: The explanation for why the correct answer is
            correct.
        needs_comment - bool: True if the participant should be asked why
            they picked what they did after they answer the question.
        num_media_items - int: How many MediaItems should be shown when
            displaying this question

    Relationships:
       O2M with Choice (parent)
       M2M with Dataset - if empty, this Question is universal
    """

    question = db.Column(db.String(200))
    choices = db.relationship("Choice", backref="question")
    datasets = db.relationship("Dataset", secondary=question_dataset_table)
    explanation = db.Column(db.String(200))
    num_media_items = db.Column(db.Integer, nullable=False)
    needs_comment = db.Column(db.Boolean())

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
    choice = db.Column(db.String(200), nullable=False)
    label = db.Column(db.String(3))
    correct = db.Column(db.Boolean)

    question_id = db.Column(db.Integer, db.ForeignKey("activity.id"))
    assignments = db.relationship("Assignment", backref="choice")


class MediaItem(Base):
    """A MediaItem is any aid to be shown when displaying an assignment. It can
    be text, image, videos, sound, whatever. Specific types should subclass
    this class and define their own fields needed for rendering.

    Attributes:
        flash_duration - integer: How long to display the MediaItem (-1 for
            indefinitely)
        name - string: Name for this Media Item

    Relationships:
        M2M with Assignment
        M2O with Dataset (child)
    """

    assignments = db.relationship(
        "Assignment",
        secondary=assignment_media_item_table)
    flash_duration = db.Column(db.Integer, nullable=False, default=-1,
                               info={"label": "Flash duration"})
    dataset_id = db.Column(db.Integer, db.ForeignKey("dataset.id"))
    type = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(100), nullable=False,
                     info={"label": "Name"},
                     default="New media item")

    __mapper_args__ = {
        'polymorphic_identity': 'media_item',
        'polymorphic_on': type
    }


class Graph(MediaItem):
    """A Graph is an image file located on the server that may be shown in
    conjunction with an Assignment.

    Attributes:
        filename - string: Filename of the graph
    """

    path = db.Column(db.String(200), nullable=False)

    def filename(self):
        """Return the filename of this graph.
        """
        return os.path.split(os.path.basename(self.path))[1]

    __mapper_args__ = {
        'polymorphic_identity': 'graph'
    }


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
    blurb = db.Column(db.String(500))

    activities = db.relationship("Activity",
                                 secondary=activity_experiment_table)
    participant_experiments = db.relationship("ParticipantExperiment",
                                              backref="experiment")
    assignments = db.relationship("Assignment", backref="experiment")


class Dataset(Base):
    """A Dataset represents some data that MediaItems are based on.

    Attributes:
        name - string
        uri - A path or descriptor of where this dataset is located.

    Relationships:
        O2M with MediaItem (parent)
        M2M with Question
        M2M with Participant
    """
    name = db.Column(db.String(100))
    uri = db.Column(db.String(200))

    media_items = db.relationship("MediaItem", backref="dataset")
    questions = db.relationship("Question", secondary=question_dataset_table)
    participant = db.relationship("Participant",
                                  secondary=participant_dataset_table)
