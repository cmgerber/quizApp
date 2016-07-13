"""Forms for the activities blueprint.
"""

from flask_wtf import Form
from wtforms import StringField, DateTimeField, SubmitField, \
    RadioField, SelectMultipleField, TextAreaField, IntegerField, \
    BooleanField
from wtforms.validators import DataRequired
from wtforms.widgets.core import HTMLString, CheckboxInput, ListWidget

from quizApp.forms.common import MultiCheckboxField, ListObjectForm
import pdb

class QuestionForm(Form):
    """Form that can be used for creating or updating questions.
    """

    question = TextAreaField("Question text", validators=[DataRequired()])
    num_graphs = IntegerField("Number of graphs to show",
                              validators=[DataRequired()])
    explanation = TextAreaField(
        "Explanation (displayed to explain the correct choice)")
    needs_reflection = BooleanField("Ask students for a reflection")
    submit = SubmitField("Submit")

    def populate_fields(self, question):
        """Given a question, populate the fields in this form.
        """
        self.question.data = question.question
        self.explanation.data = question.explanation
        self.needs_reflection.data = question.needs_reflection
        self.num_graphs.data = question.num_graphs

    def populate_question(self, question):
        """Given a question, populate it using the values of the fields.
        """
        question.question = self.question.data
        question.explanation = self.explanation.data
        question.needs_reflection = self.needs_reflection.data
        question.num_graphs = self.num_graphs.data


class DatasetListForm(ListObjectForm):
    """List a bunch of datasets.
    """

    def get_choice_tuple(self, dataset):
        self.objects.choices.append((str(dataset.id), dataset.name))

class ChoiceForm(Form):
    """Form for creating or updating choices.
    """
    label = StringField("Label", validators=[DataRequired()])
    choice = StringField("Choice", validators=[DataRequired()])
    correct = BooleanField("Correct?")
    submit = SubmitField("Submit")

    def populate_fields(self, choice):
        """Given a choice, populate the fields to match the choice.
        """
        self.label.data = choice.label
        self.choice.data = choice.choice
        self.correct.data = choice.correct

    def populate_choice(self, choice):
        """Given a choice, populate the choice to match the form.
        """
        choice.label = self.label.data
        choice.choice = self.choice.data
        choice.correct = self.correct.data



    def get_choice_tuple(self, choice):
        self.objects.choices.append((str(choice.id), choice.choice))
