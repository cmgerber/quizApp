"""Test the Experiments blueprint.
"""

from quizApp.models import ParticipantExperiment

from tests.factories import ExperimentFactory
from tests.auth import login_participant, get_participant, \
    login_experimenter


def test_experiments(client):
    """Make sure that the blueprint is inaccessible to users not logged in.
    """
    response = client.get("/experiments/")
    assert response.status_code == 302

    exp = ExperimentFactory()
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
    exp = ExperimentFactory()
    exp.save()
    part_exp = ParticipantExperiment(experiment_id=exp.id,
                                     participant_id=participant.id)
    part_exp.save()

    exp_url = "/experiments/" + str(exp.id)

    response = client.get("/experiments/")
    assert response.status_code == 200
    assert exp.name in response.data

    response = client.get(exp_url)
    assert response.status_code == 200
    assert exp.name in response.data
    assert exp.blurb in response.data

    response = client.get(exp_url + "/settings")
    assert response.status_code == 302

    response = client.delete(exp_url)
    assert response.status_code == 302

    response = client.put(exp_url)
    assert response.status_code == 302


def test_experiments_authed_experimenter(client, users):
    """Make sure logged in experimenters can see things.
    """
    response = login_experimenter(client)
    assert response.status_code == 200

    response = client.get("/")
    assert "Hello experimenter" in response.data

    exp = ExperimentFactory()
    exp.save()

    exp_url = "/experiments/" + str(exp.id)

    response = client.get("/experiments/")
    assert response.status_code == 200
    assert exp.name in response.data

    response = client.get(exp_url)
    assert response.status_code == 200
    assert exp.name in response.data
    assert "Start" not in response.data

    response = client.get(exp_url + "/settings")
    assert response.status_code == 200

    response = client.put(exp_url)
    assert response.status_code == 200

    response = client.delete(exp_url)
    assert response.status_code == 200


def test_experiments_delete(client, users):
    """Make sure logged in experimenters can delete expeirments.
    """
    response = login_experimenter(client)
    assert response.status_code == 200

    exp = ExperimentFactory()
    exp.save()

    exp_url = "/experiments/" + str(exp.id)

    response = client.delete(exp_url)
    assert response.status_code == 200

    response = client.get("/experiments/")
    assert response.status_code == 200
    assert exp.name not in response.data


def test_experiments_create(client, users):
    """Make sure logged in experimenters can create expeirments.
    """
    response = login_experimenter(client)
    assert response.status_code == 200

    exp = ExperimentFactory()
    datetime_format = "%Y-%m-%d %H:%M:%S"

    response = client.post("/experiments/", data=dict(
        name=exp.name,
        start=exp.start.strftime(datetime_format),
        stop=exp.stop.strftime(datetime_format),
        blurb=exp.blurb))
    assert response.status_code == 200

    response = client.get("/experiments/")
    assert response.status_code == 200
    assert exp.name in response.data
