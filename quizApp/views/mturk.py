"""These are views for interfacing with amazon mechanical turk.
"""

from flask import Blueprint, render_template, request

mturk = Blueprint("mturk", __name__, url_prefix="/mturk")


@mturk.route("/register")
def register():
    """Register this amturk user.
    """
    return render_template("mturk/register", request=request)
