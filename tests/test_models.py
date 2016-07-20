"""Run tests on the database models.
"""
import os

import pytest

from tests.factories import ExperimentFactory, ParticipantFactory, \
    ChoiceFactory
from quizApp.models import ParticipantExperiment, Assignment, Role, Activity, \
    Question, Graph


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

    activity = Activity()
    exp2.activities.append(activity)
    assignment.activity = activity
    part_exp.participant = part2

    part_exp.assignments.append(assignment)


def test_assignment_validators():
    """Test validators of the Assignment model.
    """
    assn = Assignment()
    exp = ExperimentFactory()
    activity = Activity()
    assn.experiment = exp

    with pytest.raises(AssertionError):
        assn.activity = activity

    activity.experiments.append(exp)
    assn.activity = activity

    choice = ChoiceFactory()
    question = Question()
    question.experiments.append(exp)

    assn.activity = question

    with pytest.raises(AssertionError):
        assn.choice = choice

    question.choices.append(choice)

    assn.choice = choice


def test_graph_filename():
    """Make sure graph filenames work correctly.
    """
    path = "/foo/bar/baz/"
    filename = "boo.png"

    full_path = os.path.join(path, filename)

    graph = Graph(path=full_path, name="Foobar")

    assert graph.filename() == filename
