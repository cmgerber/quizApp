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

    assert question.type in response.data


def test_read_activity(client, users):
    login_experimenter(client)

    question = SingleSelectQuestionFactory()
    question.save()

    url = "/activities/" + str(question.id)

    response = client.get(url)
    assert response.status_code == 200
    assert question.question in response.data
    assert question.explanation in response.data

    for choice in question.choices:
        assert choice.choice in response.data


def test_settings_activity(client, users):
    login_experimenter(client)

    question = SingleSelectQuestionFactory()
    question.save()

    url = "/activities/" + str(question.id) + "/settings"

    response = client.get(url)
    assert response.status_code == 200
    assert question.question in response.data
    assert question.explanation in response.data

    for choice in question.choices:
        assert choice.choice in response.data


def test_update_activity(client, users):
    login_experimenter(client)

    question = SingleSelectQuestionFactory()
    question.save()

    url = "/activities/" + str(question.id)

    new_question = SingleSelectQuestionFactory()

    response = client.put(url,
                          data={"question": new_question.question,
                                "explanation": new_question.explanation,
                                "num_media_items":
                                new_question.num_media_items}
                          )
    assert response.status_code == 200
    assert json_success(response.data)

    response = client.get(url)
    assert new_question.question in response.data
    assert new_question.explanation in response.data
