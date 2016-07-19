"""Run tests on the database models.
"""
from datetime import datetime, timedelta
import pytest

from quizApp.models import Experiment, ParticipantExperiment, Assignment, \
    Role, Participant


def test_db_rollback1():
    """Along with test_db_rollback2, ensure rollbacks are working correctly.
    """
    exp = Role(name="notaname-1")
    exp.save()
    assert Role.query.filter_by(name="notaname-1").count() == 1
    assert Role.query.filter_by(name="notaname-2").count() == 0


def test_db_rollback2():
    """Along with test_db_rollback1, ensure rollbacks are working correctly.
    """
    exp = Role(name="notaname-2")
    exp.save()
    assert Role.query.filter_by(name="notaname-1").count() == 0
    assert Role.query.filter_by(name="notaname-2").count() == 1


def test_participant_experiment_validators():
    """Make sure validators are functioning correctly.
    """
    exp1 = Experiment(name="foo", start=datetime.now(),
                      stop=datetime.now() + timedelta(days=5))
    exp2 = Experiment(name="bar", start=datetime.now(),
                      stop=datetime.now() + timedelta(days=5))

    part_exp = ParticipantExperiment(experiment=exp1)
    assignment = Assignment(experiment=exp2)

    with pytest.raises(AssertionError):
        part_exp.assignments.append(assignment)

    user1 = Participant(email="u1", password="foo")
    user2 = Participant(email="u2", password="foo")

    part_exp.experiment = exp2
    part_exp.participant = user1
    assignment.participant = user2

    with pytest.raises(AssertionError):
        part_exp.assignments.append(assignment)
