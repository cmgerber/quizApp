from flask_wtf import Form
from wtforms import StringField, DateTimeField, SubmitField, HiddenField, \
        RadioField, PasswordField
from wtforms.validators import DataRequired
from wtforms.widgets.core import HTMLString
import pdb


class LoginForm(Form):
    name = StringField("Name", validators=[DataRequired()])
    password = PasswordField("Password")
    submit = SubmitField("Login")
