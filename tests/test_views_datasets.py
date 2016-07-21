"""Tests for dataset views.
"""
import factory

from tests.helpers import json_success
from tests.auth import login_experimenter
from tests.factories import DatasetFactory
from quizApp.models import Dataset
from quizApp import db


def test_read_datasets(client, users):
    login_experimenter(client)
    datasets = factory.create_batch(DatasetFactory, 10)
    db.session.add_all(datasets)
    db.session.commit()

    response = client.get("/datasets/")
    assert response.status_code == 200
    for dataset in datasets:
        assert dataset.name in response.data


def test_create_dataset(client, users):
    login_experimenter(client)

    assert Dataset.query.count() == 0

    dataset = DatasetFactory()

    response = client.post("/datasets/", data={"name": dataset.name,
                                               "uri": dataset.uri})

    assert response.status_code == 200
    assert json_success(response.data)

    assert Dataset.query.count() == 1
    created_dataset = Dataset.query.one()

    assert created_dataset.name == dataset.name
    assert created_dataset.uri == dataset.uri

    response = client.post("/datasets/")

    assert response.status_code == 200
    assert not json_success(response.data)

    response = client.get("/datasets/")
    assert response.status_code == 200
    assert dataset.name in response.data


def test_update_dataset(client, users):
    login_experimenter(client)
    dataset = DatasetFactory()
    dataset.save()

    new_dataset = DatasetFactory()
    url = "/datasets/" + str(dataset.id)

    response = client.put(url, data={"name": new_dataset.name,
                          "uri": new_dataset.uri})
    assert response.status_code == 200
    assert json_success(response.data)

    response = client.get("/datasets/")
    assert response.status_code == 200
    assert new_dataset.name in response.data

    response = client.put(url)
    assert response.status_code == 200
    assert not json_success(response.data)


def test_delete_dataset(client, users):
    login_experimenter(client)
    dataset = DatasetFactory()
    dataset.save()

    url = "/datasets/" + str(dataset.id)

    response = client.delete(url)
    assert response.status_code == 200
    assert json_success(response.data)

    response = client.get("/datasets/")
    assert response.status_code == 200
    assert dataset.name not in response.data
