"""Test the Experiments blueprint.
"""
import pdb
from datetime import datetime, timedelta

from quizApp.models import Experiment, ParticipantExperiment

from tests.auth import login_participant, get_participant, \
    login_experimenter


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
    exp = Experiment(name="foo", start=datetime.now(),
                     stop=datetime.now() + timedelta(days=5),
                     blurb="this is a blurb")
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
    
    exp = Experiment(name="foo", start=datetime.now(),
                     stop=datetime.now() + timedelta(days=5))
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
    
    exp = Experiment(name="foo", start=datetime.now(),
                     stop=datetime.now() + timedelta(days=5))
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

    exp_name = "foo"
    exp_start = datetime.now()
    exp_stop = datetime.now() + timedelta(days=4)
    exp_blurb = "behwavbuila"
    datetime_format = "%Y-%m-%d %H:%M:%S"

    pdb.set_trace()
    response = client.post("/experiments/", data=dict(
        name=exp_name,
        start=exp_start.strftime(datetime_format),
        stop=exp_stop.strftime(datetime_format),
        blurb=exp_blurb))
    assert response.status_code == 200
    
    response = client.get("/experiments/")
    assert response.status_code == 200
    assert exp_name in response.data
