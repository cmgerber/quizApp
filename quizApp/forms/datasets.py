"""Forms for dataset views.
"""

from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from wtforms_alchemy import ModelForm
from quizApp.models import Graph
from quizApp.forms.common import OrderFormMixin


class DatasetForm(Form):
    """Form for creation or update of a dataset.
    """

    name = StringField("Name", validators=[DataRequired()])
    uri = StringField("URI", validators=[DataRequired()])
    submit = SubmitField("Submit")

    def populate_dataset(self, dataset):
        """Given a Dataset instance, update its fields to reflect the state of
        the form.
        """
        dataset.name = self.name.data
        dataset.uri = self.uri.data

    def populate_fields(self, dataset):
        """Given a Dataset instance, update the form's state to reflect its
        fields.
        """
        self.name.data = dataset.name
        self.uri.data = dataset.uri


class GraphForm(OrderFormMixin, ModelForm):
    """Form for updating Graph objects.
    """
    class Meta(object):
        """Specify model and field order.
        """
        model = Graph
        exclude = ['path']
        order = ('*', 'submit')

    submit = SubmitField("Submit")
