"""Forms for the Experiments blueprint.
"""

from flask_wtf import Form
from wtforms import StringField, DateTimeField, SubmitField, \
        RadioField, TextAreaField
from wtforms.validators import DataRequired
from wtforms.widgets.core import HTMLString, html_params

from quizApp.forms.common import MultiCheckboxField
import pdb

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


class ActivityListForm(Form):
    """Form to show a selectable list of Activities.
    """
    activities = MultiCheckboxField(validators=[DataRequired()], choices=[])
    submit = SubmitField("Submit")

    def populate_activities(self, activities_set):
        """Given a list of Activities, populate the activities field with
        choices.
        """
        activities_mapping = {}
        for activity in activities_set:
            activities_mapping[str(activity.id)] = activity
            if "question" in activity.type:
                choice_tuple = (str(activity.id), activity.question)
            else:
                choice_tuple = (str(activity.id), "-")
            self.activities.choices.append(choice_tuple)
        return activities_mapping

    def reset_activities(self):
        """Reset the list of activities - sometimes necessary in strange
        situations
        """
        self.activities.choices = []
