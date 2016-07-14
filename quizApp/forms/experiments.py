"""Forms for the Experiments blueprint.
"""

from flask_wtf import Form
from wtforms import StringField, DateTimeField, SubmitField, \
        RadioField, TextAreaField
from wtforms.validators import DataRequired

from quizApp.forms.common import MultiCheckboxField


def get_question_form(question):
    """Given a question type, return the proper form.
    """
    if "scale" in question.type:
        return ScaleForm()
    else:
        return MultipleChoiceForm()


class LikertField(RadioField):
    """Field for displaying a Likert scale. The only difference from a
    RadioField is how its rendered, so this class is for rendering purposes.
    """
    pass


class QuestionForm(Form):
    """Form for rendering a general Question.
    """
    submit = SubmitField("Submit")
    reflection = TextAreaField()

    def populate_choices(self, choice_pool):
        """Child classes should implement this themselves for choice selection.
        """
        pass


class MultipleChoiceForm(QuestionForm):
    """Form for rendering a multiple choice question with radio buttons.
    """
    choices = RadioField(validators=[DataRequired()], choices=[])

    def populate_choices(self, choice_pool):
        """Given a pool of choices, populate the choices field.
        """
        self.choices.choices = [(str(c.id), c.choice) for c in choice_pool]


class ScaleForm(MultipleChoiceForm):
    """Form for rendering a likert scale question.
    """
    choices = LikertField(validators=[DataRequired()])


class CreateExperimentForm(Form):
    """Form for creating or updating an experiment's properties.
    """
    name = StringField("Name", validators=[DataRequired()])
    start = DateTimeField("Start time", validators=[DataRequired()])
    stop = DateTimeField("Stop time", validators=[DataRequired()])
    submit = SubmitField("Submit")
    blurb = TextAreaField("Blurb")

    def populate_experiment(self, experiment):
        """Given an Experiment instance, set its values to those contained by
        the form.
        """

        experiment.name = self.name.data
        experiment.start = self.start.data
        experiment.stop = self.stop.data
        experiment.blurb = self.blurb.data

    def populate_fields(self, experiment):
        """Given an Experiment instance, set this form's fields' values to
        those contained by the experiment.
        """

        self.name.data = experiment.name
        self.start.data = experiment.start
        self.stop.data = experiment.stop
        self.blurb.data = experiment.blurb
