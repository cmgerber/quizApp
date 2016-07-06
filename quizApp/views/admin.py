from flask import current_app, Blueprint, render_template, flash, redirect, \
        url_for
from quizApp import login_manager, db
from flask_login import login_required, current_user, logout_user, login_user
from quizApp.forms.admin import LoginForm
from quizApp.models import User

admin = Blueprint('admin', __name__, url_prefix='/admin')

@login_manager.user_loader
def user_loader(user_id):
    """Load the given user id.
    """
    return User.query.get(int(user_id))


@admin.route("/logout", methods=["GET"])
@login_required
def logout():
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return redirect(url_for("core.home"))

@admin.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
       user = User.query.get(int(form.name.data))
       if user:
           login_user(user)
           flash("Logged in successfully.")
           return redirect(url_for("core.home"))

    return render_template("admin/login.html", form=form)
