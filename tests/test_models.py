"""Run tests on the database models.
"""

from quizApp.models import Experiment


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
