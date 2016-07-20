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


class ActivityFactory(factory.Factory):
    class Meta:
        model = models.Activity

    type = factory.Iterator(["question", "question_mc_singleselect",
                             "question_mc_singleselect_scale"])
    category = factory.Faker("text")


class AssignmentFactory(factory.Factory):
    class Meta:
        model = models.Assignment

    skipped = factory.Faker("boolean")
    comment = factory.Faker("text")
    choice_order = factory.Faker("text")


class ParticipantExperimentFactory(factory.Factory):
    class Meta:
        model = models.ParticipantExperiment

    progress = factory.Faker("pyint")
    complete = factory.Faker("boolean")


def create_experiment(num_activities, participants, activity_types=[]):
    experiment = ExperimentFactory()
    num_participants = len(participants)
    participant_experiments = []
    
    for participant in participants:
        part_exp = ParticipantExperimentFactory()
        part_exp.participant = participant
        part_exp.experiment = experiment
        participant_experiments.append(part_exp)

    for i in xrange(0, num_activities*num_participants):
        participant = participants[i % num_participants]
        part_exp = participant_experiments[i % num_participants]

        if activity_types:
            activity = ActivityFactory(random.choice(activity_types)) 
        else:
            activity = ActivityFactory()

        assignment = AssignmentFactory()
        
        activity.experiments.append(experiment)
         
        assignment.experiment = experiment
        assignment.participant = participant
        assignment.activity = activity

        part_exp.assignments.append(assignment)

    return experiment
