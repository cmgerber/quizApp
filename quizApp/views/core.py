"""This blueprint takes care of rendering static pages outside of the other
blueprints.
"""
import os

from flask import Blueprint, render_template, send_file
from openpyxl import Workbook
from sqlalchemy import inspect
from sqlalchemy.orm.properties import ColumnProperty

from quizApp import models
from quizApp.config import basedir


core = Blueprint("core", __name__, url_prefix="/")


# homepage
@core.route('')
def home():
    """Display the homepage."""
    return render_template('core/index.html',
                           is_home=True)


@core.route('export')
def export():
    """Send the user a breakddown of datasets, activities, etc. for use in
    making assignments.
    """

    sheets = {
        "Datasets": models.Dataset.query,
        "Activities": models.Activity.query,
        "Experiments": models.Experiment.query,
        "Media items": models.MediaItem.query,
    }

    workbook = Workbook()
    workbook.remove_sheet(workbook.active)

    for sheet_name, query in sheets.iteritems():
        current_sheet = workbook.create_sheet()
        current_sheet.title = sheet_name
        sheet = object_list_to_sheet(query.all())
        for r in range(1, len(sheet) + 1):
            for c in range(1, len(sheet[0]) + 1):
                current_sheet.cell(row=r, column=c).value = sheet[r - 1][c - 1]

    file_name = os.path.join(basedir, "export.xlsx")
    workbook.save(file_name)
    return send_file(file_name, as_attachment=True)


def object_list_to_sheet(object_list):
    """Given a list of objects, iterate over all of them and create an xlsx
    sheet.

    The first row returned will be a header row. All fields will be included
    unless a field contains export-include: False in its info attibute.
    """
    headers = []
    rows = []

    for obj in object_list:
        row = [""]*len(headers)
        for column, prop in inspect(type(obj)).attrs.items():
            try:
                include = prop.info["export_include"]
            except KeyError:
                include = True

            if not isinstance(prop, ColumnProperty):
                continue

            if not include:
                continue

            if column not in headers:
                headers.append(column)
                row.append("")
            index = headers.index(column)

            row[index] = getattr(obj, column)
        rows.append(row)
    sheet = [headers]
    sheet.extend(rows)
    return sheet
