from flask_wtf import Form
from wtforms import StringField, DateTimeField, SubmitField, HiddenField, \
        RadioField
from wtforms.validators import DataRequired

class DateTimeWidget(object):
    def __call__(self, field, **kwargs):
        output = ('<div class="input-group date" id="{}">'
                  '<input type="text" class="form-control {}"'
                  '    name="{}"/>'
                  '<span class="input-group-addon">'
                  '    <span class="glyphicon'
                  '    glyphicon-calendar"></span>'
                  '    </span>'
                  '</div>'
                  '<script type="text/javascript">'
                  '    $(function () {{'
                  '        $("#{}").datetimepicker({{'
                  '             format: "YYYY-MM-DD HH:mm:ss"'
                  '         }});'
                  '    }});'
                  '</script>').format(field.id,
                                      kwargs.pop("class_", ""),
                                      field.name,
                                      field.id)
        return u'' + output

class CreateExperimentForm(Form):
    name = StringField("Name", validators=[DataRequired()])
    start = DateTimeField("Start time", widget=DateTimeWidget(),
                          validators=[DataRequired()])
    stop = DateTimeField("Stop time", widget=DateTimeWidget(),
                        validators=[DataRequired()])
    submit = SubmitField("Submit")

class DeleteExperimentForm(Form):
    exp_id = HiddenField()
    submit = SubmitField("Submit")

class MultipleChoiceForm(Form):
    answers = RadioField(validators=[DataRequired()])
