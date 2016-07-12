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


class DatasetListForm(ListObjectForm):
    """List a bunch of datasets.
    """

    def get_choice_tuple(self, dataset):
        self.objects.choices.append((str(dataset.id), dataset.name))

class ChoiceListForm(ListObjectForm):
    """List choices.
    """

    def get_choice_tuple(self, choice):
        self.objects.choices.append((str(choice.id), choice.choice))
