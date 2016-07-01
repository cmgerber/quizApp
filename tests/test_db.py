from quizApp.models import Question
from quizApp import db, app
import pytest

@pytest.yield_fixture
def app():
    with app.app_context():
        yield _app

@pytest.yield_fixture
def db(app, monkeypatch):
    connection = db.engine.connect()
    transaction = connection.begin()

    monkeypatch.setattr(_db, 'get_engine', lambda *args: connection)

    try:
        yield db
    finally:
        db.session.remove()
        transaction.rollback()
        connection.close()

def test_environment(db):
    models.Question.query.all()
    assert 0
