"""This script creates fixtures so that the database is rolled back between
unit tests. This is considerably faster than drop_all create_all after every
test.
"""

import pytest

from clear_db import clear_db
from quizApp import create_app
from quizApp import db


@pytest.fixture(scope="session")
def app(request):
    """Create an app fixture that has a special context for easy rollback.
    """
    app_ = create_app("testing")

    ctx = app_.app_context()
    ctx.push()

    def teardown():
        """After this app is used, remove the context.
        """
        ctx.pop()

    request.addfinalizer(teardown)

    return app_


@pytest.yield_fixture(scope="session")
def client(request, app):
    """Get a testing client from the app.
    """
    with app.test_client() as client_:
        yield client_


@pytest.fixture(scope="session", autouse=True)
def setup_db(request, app):
    """Initialize database for testing.
    """
    clear_db()
    db.create_all()


@pytest.fixture(autouse=True)
def dbsession(request, monkeypatch):
    """Provide a patched database session that rolls back after each test.
    """
    request.addfinalizer(db.session.remove)

    monkeypatch.setattr(db.session, "commit", db.session.flush)
    monkeypatch.setattr(db.session, "remove", lambda: None)
