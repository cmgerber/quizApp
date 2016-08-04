"""Test amazon turk views.
"""
from quizApp.models import Participant

from tests.factories import ExperimentFactory


def test_register(client, users):
    experiment = ExperimentFactory()
    experiment.save()

    response = client.get("/mturk/register?experiment_id={}".
                          format(experiment.id))
    assert response.status_code == 200
    assert experiment.blurb in response.data

    response = client.get("/mturk/register")
    assert response.status_code == 400

    response = client.get(("/mturk/register?experiment_id={}"
                           "&workerId=4fsa&assignmentId=4&turkSubmitTo=4").
                          format(experiment.id))

    assert response.status_code == 200
    assert "/experiments" in response.data

    # one from users fixture, one from views
    assert Participant.query.count() == 2

    response = client.get("/mturk/register?experiment_id={}&workerId=4fsa".
                          format(experiment.id))

    assert response.status_code == 200
    assert Participant.query.count() == 2
