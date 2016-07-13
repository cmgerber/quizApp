"""Forms for the Experiments blueprint.
"""

from flask_wtf import Form
from wtforms import StringField, DateTimeField, SubmitField, \
        RadioField, TextAreaField
from wtforms.validators import DataRequired
from wtforms.widgets.core import HTMLString

from quizApp.forms.common import MultiCheckboxField


def get_question_form(question):
    """Given a question type, return the proper form.
    """
    if "scale" in question.type:
        return ScaleForm()
    else:
        return MultipleChoiceForm()


class LikertWidget(object):
    """A widget that displays a Likert scale of radio buttons.
    """
    input_type = "likert"

    def __call__(self, field, **kwargs):
        # Likert widget from Pete Fectau's example
        output = "<ul class='likert'>\n"
        for choice in field.choices:
            checked = ""
            if field.default == choice[0]:
                checked = "checked"
            output += ('<li>\n'
                       '  <input type="radio" name="{}" value="{}" {}>\n'
                       '  <label>{}</label>\n'
                       '</li>\n').format(field.name, choice[0], checked, choice[1])

        output += "</ul>\n"
        return HTMLString(output)


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
    choices = RadioField(validators=[DataRequired()], widget=LikertWidget())


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
