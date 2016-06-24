"""Custom jinja filters for the project.
"""
from quizApp import app

@app.template_filter("datetime_format")
def datetime_format_filter(value, fmt="%Y-%m-%d %H:%M:%S"):
    """Format the value (a datetime) according to fmt with strftime.
    """
    return value.strftime(fmt)
