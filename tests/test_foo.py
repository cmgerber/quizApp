from quizApp import db
from quizApp import models

def test_environment():
    models.Question.query.all()
    assert 0
