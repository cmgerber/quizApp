"""Tests for core views.
"""
import tempfile
from openpyxl import load_workbook

from tests.auth import login_experimenter


def test_import_template(client, users):
    """Make sure we can get an import template.
    """
    login_experimenter(client)

    response = client.get("/import_template")
    outfile = tempfile.TemporaryFile()
    outfile.write(response.data)

    workbook = load_workbook(outfile)

    assert len(workbook.get_sheet_names())
