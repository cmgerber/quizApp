import os
import pytest

from quizApp import create_app
from quizApp import db 
from quizApp.models import Experiment

@pytest.fixture(scope="session")
def app(request):
    app = create_app("testing")

    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)

    return app

@pytest.fixture(scope="session", autouse=True)
def setup_db(request, app):
    db.drop_all()
    db.create_all()

@pytest.fixture(autouse=True)
def dbsession(request, monkeypatch):
    request.addfinalizer(db.session.remove)

    monkeypatch.setattr(db.session, "commit", db.session.flush)
    monkeypatch.setattr(db.session, "remove", lambda: None)
