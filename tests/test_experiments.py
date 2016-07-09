"""Test the Experiments blueprint.
"""

from quizApp.models import Experiment


def test_experiments(client):
    """Make sure that the blueprint is inaccessible to users not logged in.
    """
    response = client.get("/experiments")
    assert response.status_code == 302

    exp = Experiment(name="foo")
    exp.save()

    response = client.get("/experiments/" + str(exp.id))
    assert response.status_code == 302

    response = client.delete("/experiments/" + str(exp.id))
    assert response.status_code == 302
