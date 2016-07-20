"""Various factories, useful for writing less boilerplate when testing.
"""

import factory
from quizApp import models
from datetime import datetime, timedelta


class ExperimentFactory(factory.Factory):
    class Meta:
        model = models.Experiment

    name = factory.Faker('name')
    blurb = factory.Faker('text')
    start = datetime.now()
    stop = datetime.now() + timedelta(days=5)


class ParticipantFactory(factory.Factory):
    class Meta:
        model = models.Participant

    email = factory.Faker('email')
    password = factory.Faker('password')


class ChoiceFactory(factory.Factory):
    class Meta:
        model = models.Choice

    choice = factory.Faker('text')
    label = factory.Faker('text')
    correct = factory.Faker("boolean")
