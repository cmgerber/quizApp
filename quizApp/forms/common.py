"""Common forms or form elements live here.
"""

from flask_wtf import Form
from wtforms import SubmitField, SelectMultipleField, SelectField
from wtforms.validators import DataRequired
from wtforms.widgets.core import CheckboxInput, ListWidget


class MultiCheckboxField(SelectMultipleField):
    """Like a SelectMultipleField, but use checkboxes instead,
    """
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class ListObjectForm(Form):
    """A form that has a MultiCheckboxField of some objet.
    """
    objects = MultiCheckboxField(validators=[DataRequired()])
    submit = SubmitField("Submit")

    def reset_objects(self):
        """Sometimes choices have to be reset.
        """
        self.objects.choices = []

    def populate_objects(self, object_pool):
        """Given a list of objects, populate the object field with
        choices.
        """
        if not self.objects.choices:
            self.objects.choices = []

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


class ObjectTypeForm(Form):
    """Select an object type from a drop down menu.
    """
    object_type = SelectField("Type")
    submit = SubmitField("Submit")

    def populate_object_type(self, mapping):
        """Given a mapping of object types to human readable names, populate
        the object_type field.
        """
        self.object_type.choices = [(k, v) for k, v in mapping.iteritems()]
