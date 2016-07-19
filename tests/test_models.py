"""Run tests on the database models.
"""

from quizApp import db
from quizApp.models import Experiment, ParticipantExperiment, Assignment


def test_db_rollback1():
    """Along with test_db_rollback2, ensure rollbacks are working correctly.
    """
    exp = Experiment(name="notaname-1")
    exp.save()
    assert Experiment.query.filter_by(name="notaname-1").count() == 1
    assert Experiment.query.filter_by(name="notaname-2").count() == 0


def test_db_rollback2():
    """Along with test_db_rollback1, ensure rollbacks are working correctly.
    """
    exp = Experiment(name="notaname-2")
    exp.save()
    assert Experiment.query.filter_by(name="notaname-1").count() == 0
    assert Experiment.query.filter_by(name="notaname-2").count() == 1


def test_validators():
    """Make sure validators are functioning correctly.
    """
    exp1 = Experiment(name="foo")
    exp2 = Experiment(name="bar")
    part_exp = ParticipantExperiment(experiment=exp1)
    assignment = Assignment(experiment=exp2)
    part_exp.assignments.append(assignment)
    db.session.add_all(exp1, exp2, part_exp, assignment)
    db.session.commit()



