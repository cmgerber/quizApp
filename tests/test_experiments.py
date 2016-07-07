from quizApp.models import Experiment, Activity
import json

from tests import conftest

def test_experiments(client):
    response = client.get("/experiments")
    assert response.status_code == 401

    exp = Experiment(name="foo")
    exp.save()

    response = client.get("/experiments/" + str(exp.id))
    assert response.status_code == 401

    #response = client.put("/experiments/" + str(exp.id))
    #assert response.status_code == 401

    response = client.delete("/experiments/" + str(exp.id))
    assert response.status_code == 401
