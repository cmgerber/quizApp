"""These are views for interfacing with amazon mechanical turk.
"""

from flask import Blueprint, render_template, request

mturk = Blueprint("mturk", __name__, url_prefix="/mturk")


@mturk.route("/register")
def register():
    """Register this amturk user.

    From the URL arguments, grab the user ID from amazon and create a user
    record in our database. Log in the user. Redirect them to the experiment
    landing page.
    """
    return render_template("mturk/register.html", request=request)
