"""Forms for the activities blueprint.
"""

from flask_wtf import Form
from wtforms import StringField, SubmitField, \
    TextAreaField, IntegerField, BooleanField
from wtforms.validators import DataRequired

from quizApp.forms.common import ListObjectForm


class QuestionForm(Form):
    """Form that can be used for creating or updating questions.
    """

    question = TextAreaField("Question text", validators=[DataRequired()])
    num_media_items = IntegerField("Number of media items to show",
                                   validators=[DataRequired()])
    explanation = TextAreaField(
        "Explanation (displayed to explain the correct choice)")
    needs_comment = BooleanField("Ask students for an optional comment")
    submit = SubmitField("Submit")

    def populate_fields(self, question):
        """Given a question, populate the fields in this form.
        """
        self.question.data = question.question
        self.explanation.data = question.explanation
        self.needs_comment.data = question.needs_comment
        self.num_media_items.data = question.num_media_items

    def populate_question(self, question):
        """Given a question, populate it using the values of the fields.
        """
        question.question = self.question.data
        question.explanation = self.explanation.data
        question.needs_comment = self.needs_comment.data
        question.num_media_items = self.num_media_items.data


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
        """Return the choice tuple for this choice.
        """
        self.objects.choices.append((str(choice.id), choice.choice))
