"""Custom jinja filters for the project.
"""
from quizApp import app
from flask import Markup, url_for
import os

@app.template_filter("datetime_format")
def datetime_format_filter(value, fmt="%Y-%m-%d %H:%M:%S"):
    """Format the value (a datetime) according to fmt with strftime.
    """
    return value.strftime(fmt)

@app.template_filter("graph_to_img")
def graph_to_img_filter(graph):
    """Given a graph, return html to display it.
    """
    graph_path = url_for('static', filename=os.path.join("graphs/",
                                                         graph.filename))

    return Markup("<img src='" + graph_path + "' \>")
