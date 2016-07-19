"""Run tests on the database models.
"""
import pytest

from tests.factories import ExperimentFactory, ParticipantFactory
from quizApp.models import ParticipantExperiment, Assignment, Role


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
    exp1 = ExperimentFactory()
    exp2 = ExperimentFactory()

    part_exp = ParticipantExperiment(experiment=exp1)
    assignment = Assignment(experiment=exp2)

    with pytest.raises(AssertionError):
        part_exp.assignments.append(assignment)

    part1 = ParticipantFactory()
    part2 = ParticipantFactory()

    part_exp.experiment = exp2
    part_exp.participant = part1
    assignment.participant = part2

    with pytest.raises(AssertionError):
        part_exp.assignments.append(assignment)
