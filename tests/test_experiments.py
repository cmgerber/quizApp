"""Test the Experiments blueprint.
"""
from datetime import datetime

from quizApp.models import Experiment, ParticipantExperiment

from tests.auth import login_participant, get_participant


def test_experiments(client):
    """Make sure that the blueprint is inaccessible to users not logged in.
    """
    response = client.get("/experiments/")
    assert response.status_code == 302

    exp = Experiment(name="foo")
    exp.save()

    response = client.get("/experiments/" + str(exp.id))
    assert response.status_code == 302

    response = client.delete("/experiments/" + str(exp.id))
    assert response.status_code == 302


def test_experiments_authed_participant(client, users):
    """Make sure logged in participants can see things.
    """
    response = login_participant(client)
    assert response.status_code == 200

    response = client.get("/")
    assert "Hello participant" in response.data

    participant = get_participant()
    exp = Experiment(name="foo", start=datetime.now(), stop=datetime.now())
    exp.save()
    part_exp = ParticipantExperiment(experiment_id=exp.id,
                                     participant_id=participant.id)
    part_exp.save()

    exp_url = "/experiments/" + str(exp.id)

    response = client.get("/experiments/")
    assert response.status_code == 200
    assert "foo" in response.data

    response = client.get(exp_url)
    assert response.status_code == 200
    assert "foo" in response.data
    # assert "Start" in response.data

    response = client.get(exp_url + "/settings")
    assert response.status_code == 302

    response = client.delete(exp_url)
    assert response.status_code == 302

    response = client.put(exp_url)
    assert response.status_code == 302

    response = client.put(exp_url + "/activities")
    assert response.status_code == 302
