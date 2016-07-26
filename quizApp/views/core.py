"""This blueprint takes care of rendering static pages outside of the other
blueprints.
"""
import os
import pdb

from flask import Blueprint, render_template, send_file
from openpyxl import Workbook
from sqlalchemy import inspect
from sqlalchemy.orm.properties import ColumnProperty, RelationshipProperty
from flask_security import roles_required

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
@roles_required("experimenter")
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
        pdb.set_trace()
        current_sheet = workbook.create_sheet()
        current_sheet.title = sheet_name
        sheet_data = object_list_to_sheet(query.all())
        write_list_to_sheet(sheet_data, current_sheet)

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
            include = prop.info.get("export_include", True)

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


@core.route('import_template')
@roles_required("experimenter")
def import_template():
    """Send the user a blank excel sheet that can be filled out and used to
    populate an experiment's activity list.
    """

    sheets = {
        "Assignments": models.Assignment,
        "Participant Experiments": models.ParticipantExperiment
    }

    documentation = [
        ["Do not modify the first row in every sheet!"],
        ["Simply add in your data in the rows undeneath it."],
        ["Use IDs from the export sheet to populate relationship columns."],
        [("If you want multiple objects in a relation, separate the IDs using"
          "commas.")],
    ]

    workbook = Workbook()
    workbook.remove_sheet(workbook.active)

    for sheet_name, model in sheets.iteritems():
        current_sheet = workbook.create_sheet()
        current_sheet.title = sheet_name
        headers = model_to_sheet_headers(model)
        write_list_to_sheet(headers, current_sheet)

    current_sheet = workbook.create_sheet()
    current_sheet.title = "Documentation"
    write_list_to_sheet(documentation, current_sheet)

    file_name = os.path.join(basedir, "import-template.xlsx")
    workbook.save(file_name)
    return send_file(file_name, as_attachment=True)


def model_to_sheet_headers(model):
    """Given a model, put all columns whose info contains "export-include":
    True into a list of headers.
    """

    headers = []
    for column, prop in inspect(model).attrs.items():
        if isinstance(prop, ColumnProperty):
            info = prop.columns[0].info
        elif isinstance(prop, RelationshipProperty):
            info = prop.info

        include = info.get("import_include", False)

        if include:
            headers.append(column)

    return [headers]


def write_list_to_sheet(data_list, sheet):
    """Given a list and a sheet, write out the list to the sheet.
    The list should be two dimensional, with each list in the list representing
    a row.
    """

    for r in xrange(1, len(data_list) + 1):
        for c in xrange(1, len(data_list[r - 1]) + 1):
            sheet.cell(row=r, column=c).value = data_list[r - 1][c - 1]
