"""Test activity views.
"""

import factory

from tests.auth import login_experimenter
from tests.factories import ActivityFactory, SingleSelectQuestionFactory
from tests.helpers import json_success
from quizApp import db


def test_read_activities(client, users):
    login_experimenter(client)
    activities = factory.create_batch(ActivityFactory, 10)
    db.session.add_all(activities)
    db.session.commit()

    response = client.get("/activities/")

    for activity in activities:
        assert activity.category in response.data
        assert str(activity.id) in response.data


def test_create_activity(client, users):
    login_experimenter(client)

    question = SingleSelectQuestionFactory()

    response = client.post("/activities/")
    assert response.status_code == 200
    assert not json_success(response.data)

    response = client.post("/activities/",
                           data={"object_type": question.type})
    assert response.status_code == 200
    assert json_success(response.data)

    response = client.get("/activities/")

    assert question.text in response.data
