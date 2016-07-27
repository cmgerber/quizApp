"""This blueprint takes care of rendering static pages outside of the other
blueprints.
"""
import os

from flask import Blueprint, render_template, send_file
from openpyxl import Workbook
from flask_security import roles_required

from quizApp import models
from quizApp.config import basedir
from quizApp.views import import_export


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
        current_sheet = workbook.create_sheet()
        current_sheet.title = sheet_name
        sheet_data = import_export.object_list_to_sheet(query.all())
        import_export.write_list_to_sheet(sheet_data, current_sheet)

    file_name = os.path.join(basedir, "export.xlsx")
    workbook.save(file_name)
    return send_file(file_name, as_attachment=True)


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
          " commas.")],
    ]

    workbook = Workbook()
    workbook.remove_sheet(workbook.active)

    for sheet_name, model in sheets.iteritems():
        current_sheet = workbook.create_sheet()
        current_sheet.title = sheet_name
        headers = import_export.model_to_sheet_headers(model)
        import_export.write_list_to_sheet(headers, current_sheet)

    current_sheet = workbook.create_sheet()
    current_sheet.title = "Documentation"
    import_export.write_list_to_sheet(documentation, current_sheet)

    file_name = os.path.join(basedir, "import-template.xlsx")
    workbook.save(file_name)
    return send_file(file_name, as_attachment=True)
