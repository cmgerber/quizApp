from quizApp import create_app
from quizApp import db 
from quizApp.models import Experiment

from tests import conftest

def test_example():
    exp = Experiment(name="notaname")
    exp.save()
    print("test 1")
    assert Experiment.query.filter_by(name="notaname").count() == 1

def test_part2():
    print("test 2")
    assert Experiment.query.filter_by(name="notaname").count() == 0
