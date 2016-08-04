"""Test amazon turk views.
"""
from quizApp.models import Participant

from tests.factories import ExperimentFactory


def test_register(client):
    experiment = ExperimentFactory()
    experiment.save()

    response = client.get("/mturk/register?experiment_id={}".
                          format(experiment.id))
    assert response.status_code == 200
    assert experiment.blurb in response.data

    response = client.get("/mturk/register")
    assert response.status_code == 400

    response = client.get("/mturk/register?experiment_id={}&workerId=4fsa".
                          format(experiment.id))

    assert response.status_code == 200
    assert "/experiments" in response.data
    assert Participant.query.count() == 1

    response = client.get("/mturk/register?experiment_id={}&workerId=4fsa".
                          format(experiment.id))

    assert response.status_code == 200
    assert Participant.query.count() == 1
