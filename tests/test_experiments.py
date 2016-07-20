"""Test the Experiments blueprint.
"""

import json

import mock

from quizApp.models import ParticipantExperiment, Assignment, Activity
from quizApp.views.experiments import get_participant_experiment_or_abort
from tests.factories import ExperimentFactory, create_experiment
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


def test_delete_experiment(client, users):
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


def test_create_experiment(client, users):
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

    response = client.post("/experiments/", data=dict(
        start=exp.start.strftime(datetime_format),
        stop=exp.stop.strftime(datetime_format),
        blurb=exp.blurb))
    data = json.loads(response.data)
    assert data["success"] == 0
    assert data["errors"]


@mock.patch('quizApp.views.experiments.abort', autospec=True)
def test_get_participant_experiment_or_abort(abort_mock, client):
    """Make sure get_participant_experiment_or_abort actually aborts.
    """
    get_participant_experiment_or_abort(5, 500)

    abort_mock.assert_called_once_with(500)


def test_read_experiment(client, users):
    """Test the read_experiment method.
    """
    response = login_participant(client)
    assert response.status_code == 200

    participant = get_participant()

    exp = create_experiment(1, [participant])

    """
    assignment.experiment = exp
    exp.activities.append(activity)
    assignment.activity = activity
    assignment.participant = participant
    part_exp = ParticipantExperiment(
        participant=participant,
        experiment=exp)
    part_exp.assignments = [assignment]
    part_exp.complete = False
    part_exp.save()
    """
    url = "/experiments/" + str(exp.id)

    response = client.get(url)
    assert str(exp.participant_experiments[0].assignments[0].id) in response.data


def test_update_experiment(client, users):
    response = login_experimenter(client)
    assert response.status_code == 200
    participant = get_participant()

    experiment = create_experiment(3, [participant])
    experiment.save()

    new_exp = ExperimentFactory()

    url = "/experiments/" + str(experiment.id)

    response = client.put(url,
                          data={})
    data = json.loads(response.data)

    assert not data["success"]
    datetime_format = "%Y-%m-%d %H:%M:%S"

    response = client.put(url,
                          data={
                              "name": new_exp.name,
                              "start":
                              experiment.start.strftime(datetime_format),
                              "stop": experiment.stop.strftime(datetime_format)
                          })
    data = json.loads(response.data)

    assert data["success"]

    response = client.get("/experiments/")

    assert new_exp.name in response.data


def test_read_assignment(client, users):
    response = login_participant(client)
    assert response.status_code == 200
    participant = get_participant()

    experiment = create_experiment(3, [participant],
                                   ["question_mc_singleselect"])
    experiment.save()

    participant_experiment = experiment.participant_experiments[0]

    url = "/experiments/" + str(experiment.id) + "/assignments/"

    
