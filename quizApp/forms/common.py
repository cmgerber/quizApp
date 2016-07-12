"""Common forms or form elements live here.
"""

from flask_wtf import Form
from wtforms import StringField, DateTimeField, SubmitField, \
        RadioField, SelectMultipleField, TextAreaField
from wtforms.validators import DataRequired
from wtforms.widgets.core import HTMLString, CheckboxInput, ListWidget


class MultiCheckboxField(SelectMultipleField):
    """Like a SelectMultipleField, but use checkboxes instead,
    """
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class ListObjectForm(Form):
    """A form that has a MultiCheckboxField of some objet.
    """
    objects = MultiCheckboxField(validators=[DataRequired()], choices=[])
    submit = SubmitField("Submit")

    def reset_objects(self):
        """Sometimes choices have to be reset.
        """
        self.objects.choices = []

    def populate_objects(self, object_pool):
        """Given a list of objects, populate the object field with
        choices.
        """
        objects_mapping = {}

        for obj in object_pool:
            objects_mapping[str(obj.id)] = obj
            self.get_choice_tuple(obj)

        return objects_mapping

    def get_choice_tuple(self, obj):
        """Get a tuple for the choices of objects.
        """
        self.objects.choices.append((str(obj.id), obj.id))


class DeleteObjectForm(Form):
    """Display a button to delete some object.
    """

    submit = SubmitField("Delete")
