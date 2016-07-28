"""Functions for importing and exporting data via XLSX files.
"""
import os
from collections import OrderedDict, defaultdict
import tempfile

from openpyxl import Workbook
from sqlalchemy import inspect
from sqlalchemy.orm.interfaces import ONETOMANY, MANYTOMANY
from sqlalchemy.orm.properties import ColumnProperty, RelationshipProperty

from quizApp import db
from quizApp import models

SHEET_NAME_MAPPING = {
    "Datasets": models.Dataset,
    "Activities": models.Activity,
    "Experiments": models.Experiment,
    "Media items": models.MediaItem,
    "Participant Experiments": models.ParticipantExperiment,
    "Assignments": models.Assignment,
}


def export_to_workbook():
    """Retrieve elements from thed database and save them to a workbook.
    Return the filename of the workbook.
    """

    workbook = Workbook()
    workbook.remove_sheet(workbook.active)

    for sheet_name, model in SHEET_NAME_MAPPING.iteritems():
        current_sheet = workbook.create_sheet()
        current_sheet.title = sheet_name
        sheet_data = object_list_to_sheet(model.query.all())
        write_list_to_sheet(sheet_data, current_sheet)

    file_name = tempfile.mkstemp(".xlsx")
    os.close(file_name[0])
    workbook.save(file_name[1])
    return file_name[1]


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


def relationship_to_string(field, value):
    """Given a relationship, convert it to a comma separated list of integers.
    """
    ids = []
    direction = field.property.direction
    if direction in (MANYTOMANY, ONETOMANY):
        for obj in value:
            ids.append(str(obj.id))
        return ",".join(ids)
    elif value:
        return str(value.id)
    return ""


def field_to_string(obj, column):
    """Given an object and a column name, convert the contents
    of the column to a string. If it is a collection, return a
    comma separated list of ids.
    """
    model = type(obj)
    value = getattr(obj, column)
    field_attrs = inspect(model).attrs[column]

    if isinstance(field_attrs, RelationshipProperty):
        value = relationship_to_string(getattr(model, column), value)

    return value


def object_list_to_sheet(object_list):
    """Given a list of objects, iterate over all of them and create a list
    of lists that can be written using write_list_to_sheet.

    The first row returned will be a header row. All fields will be included
    unless a field contains export-include: False in its info attibute.
    """
    sheet = [[]]
    for obj in object_list:
        row = [""] * len(sheet[0])

        for column, prop in inspect(type(obj)).attrs.items():
            include = prop.info.get("export_include", True)

            if not include:
                continue

            if column not in sheet[0]:
                sheet[0].append(column)
                row.append("")

            index = sheet[0].index(column)

            row[index] = field_to_string(obj, column)
        sheet.append(row)
    return sheet


def populate_field(model, obj, field_name, value, pk_mapping):
    """Populate a field on a certain object based on the value from an imported
    spreadsheet.

    This may involve doing a database lookup if the field in question is a
    relationship field.

    A note on pk_mapping:

    To avoid conflicts between imported PK and existing PK, we do not
    assign PK's based on user input. However we have to store them
    because other rows in the user input may be referencing a certain PK. So
    we store them in a kind of bastard mini-database in memory while we
    are importing data.

    Arguments:
        model - The sqlalchemy model that obj is an instance of.
        obj - The object whose fields need populating.
        field_name - A string containing the name of the field that should be
        populated.
        value - The value of the field, as read from the spreadsheet.
        pk_mapping - A mapping of any objects created in this import session
        that value may refer to.
    """
    field_attrs = inspect(model).attrs[field_name]
    field = getattr(model, field_name)
    column = getattr(obj, field_name)
    if isinstance(field_attrs, RelationshipProperty):
        # This is a relationship
        remote_model = field.property.mapper.class_
        direction = field.property.direction
        if direction in (MANYTOMANY, ONETOMANY):
            values = str(value).split(",")
            for fk in values:
                fk = int(float(fk))  # goddamn stupid excel
                column.append(get_object_from_id(remote_model, fk,
                                                 pk_mapping))
        else:
            value = int(float(value))  # goddamn stupid excel
            setattr(obj, field_name, get_object_from_id(remote_model, value,
                                                        pk_mapping))
    elif field.primary_key:
        pk_mapping[model.__tablename__][int(float(value))] = obj
    elif isinstance(field_attrs, ColumnProperty):
        setattr(obj, field_name, value)


def get_object_from_id(model, obj_id, pk_mapping):
    """If the object of type model and id obj_id is in pk_mapping,
    return it. Otherwise, query the database.
    """
    try:
        return pk_mapping[model.__tablename__][obj_id]
    except KeyError:
        return model.query.get(obj_id)


def import_data_from_workbook(workbook, experiment):
    """Given an excel workbook, read in the sheets and save them to the
    database.
    TODO: this doesn't need experiment for general importation
    """
    models_mapping = OrderedDict([
        ("Participant Experiments", models.ParticipantExperiment),
        ("Assignments", models.Assignment),
    ])
    pk_mapping = defaultdict(dict)

    for sheet_name, model in models_mapping.iteritems():
        sheet = workbook.get_sheet_by_name(sheet_name)

        headers = [c.value for c in sheet.rows[0]]

        for row in sheet.rows[1:]:
            obj = model()

            associate_obj_with_experiment(obj, experiment)

            for col_index, cell in enumerate(row):
                value = cell.value
                populate_field(model, obj, headers[col_index], value,
                               pk_mapping)

            db.session.add(obj)


def associate_obj_with_experiment(obj, experiment):
    """Given an object and an experiment, associate them.

    This is mostly simple but requires some corner cases. For example, since we
    do not generate participant experiments with user IDs but rather as
    templates, we store them in Experiment.participant_experiment_templates.
    """
    if hasattr(obj, "experiments"):
        obj.experiments.append(experiment)
    elif hasattr(obj, "experiment"):
        obj.experiment = experiment
