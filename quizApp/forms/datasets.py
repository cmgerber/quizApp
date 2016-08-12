"""Forms for dataset views.
"""

from wtforms import SubmitField, FileField
from wtforms_alchemy import ModelForm
from quizApp.models import Graph, Dataset
from quizApp.forms.common import OrderFormMixin


class DatasetForm(OrderFormMixin, ModelForm):
    """Form for creation or update of a dataset.
    """
    class Meta(object):
        """Specify model and field order.
        """
        model = Dataset
        order = ('*', 'submit')

    submit = SubmitField("Save")


class GraphForm(OrderFormMixin, ModelForm):
    """Form for updating Graph objects.
    """
    class Meta(object):
        """Specify model and field order.
        """
        model = Graph
        exclude = ['path']
        order = ('*', 'submit')

    graph = FileField("Replace graph", render_kw={"accept": "image/*"})
    submit = SubmitField("Save")
