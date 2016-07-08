"""Forms for the Experiments blueprint.
"""

from flask_wtf import Form
from wtforms import StringField, DateTimeField, SubmitField, HiddenField, \
        RadioField, PasswordField
from wtforms.validators import DataRequired
from wtforms.widgets.core import HTMLString, Input


class TextAreaWidget(Input):
    """A widget that displays a multi-line textarea.
    """
    input_type = "text"

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        kwargs.setdefault('value', field._value())

        return HTMLString("<textarea %s></textarea>" %
                          self.html_params(name=field.name, **kwargs))


class LikertWidget(object):
    """A widget that displays a Likert scale of radio buttons.
    """
    input_type = "likert"

    def __call__(self, field, **kwargs):
        # Likert widget from Pete Fectau's example
        output = "<ul class='likert'>\n"
        for choice in field.choices:
            output += ('<li>\n'
                       '  <input type="radio" name="{}" value="{}">\n'
                       '  <label>{}</label>\n'
                       '</li>\n').format(field.name, choice[0], choice[1])

        output += "</ul>\n"
        return HTMLString(output)


class CreateExperimentForm(Form):
    """Form for creating or updating an experiment's properties.
    """
    name = StringField("Name", validators=[DataRequired()])
    start = DateTimeField("Start time", validators=[DataRequired()])
    stop = DateTimeField("Stop time", validators=[DataRequired()])
    submit = SubmitField("Submit")


class DeleteExperimentForm(Form):
    """Form for deleting an experiment.
    """
    exp_id = HiddenField()
    submit = SubmitField("Submit")


class QuestionForm(Form):
    """Form for rendering a general Question.
    """
    submit = SubmitField("Submit")
    reflection = StringField(widget=TextAreaWidget())

    def populate_answers(self, answer_pool):
        """Child classes should implement this themselves for choice selection.
        """
        pass


class MultipleChoiceForm(QuestionForm):
    """Form for rendering a multiple choice question with radio buttons.
    """
    answers = RadioField(validators=[DataRequired()])

    def populate_answers(self, choice_pool):
        """Given a pool of choices, populate the answers field.
        """
        self.answers.choices = [(str(c.id), c.choice) for c in choice_pool]


class ScaleForm(MultipleChoiceForm):
    """Form for rendering a likert scale question.
    """
    answers = RadioField(validators=[DataRequired()], widget=LikertWidget())


class LoginForm(Form):
    """Form for logging in.
    """
    name = StringField("Name", validators=[DataRequired()])
    password = PasswordField("Password")
    submit = SubmitField("Login")
