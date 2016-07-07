#!/bin/env python2

"""Using excel files, populate the database with some placeholder data.
"""

from quizApp import create_app
from sqlalchemy.engine import reflection
from sqlalchemy.schema import MetaData, Table, DropTable, DropConstraint, \
        ForeignKeyConstraint
from sqlalchemy import and_
from datetime import datetime, timedelta
import os
from sqlalchemy.orm.exc import NoResultFound
import csv
from quizApp.models import Question, Assignment, ParticipantExperiment, \
    Participant, Graph, Experiment, User, Dataset, Choice, Role
from quizApp import db
import pdb
import random

app = create_app("development")

def clear_db():
    #https://bitbucket.org/zzzeek/sqlalchemy/wiki/UsageRecipes/DropEverything
    inspector = reflection.Inspector.from_engine(db.engine)
    metadata = MetaData()
    tbs = []
    all_fks = []

    for table_name in inspector.get_table_names():
        fks = []
        for fk in inspector.get_foreign_keys(table_name):
            if not fk['name']:
                continue
            fks.append(ForeignKeyConstraint((),(), name=fk['name']))
        t = Table(table_name, metadata, *fks)
        tbs.append(t)
        all_fks.extend(fks)

    conn = db.engine.connect()
    trans = conn.begin()
    for fkc in all_fks:
        conn.execute(DropConstraint(fkc))

    for table in tbs:
        conn.execute(DropTable(table))
    trans.commit()

    db.create_all()

def get_experiments():
    pre_test = Experiment(name="pre_test",
                          start=datetime.now(),
                          stop=datetime.now() + timedelta(days=3))

    test = Experiment(name="test",
                      start=datetime.now(),
                      stop=datetime.now() + timedelta(days=5))

    post_test = Experiment(name="post_test",
                           start=datetime.now() + timedelta(days=-3),
                           stop=datetime.now())


    db.session.add(pre_test)
    db.session.add(test)
    db.session.add(post_test)
    db.session.commit()



DATA_ROOT = "quizApp/data/"

question_type_mapping = {"multiple_choice": "question_mc_singleselect",
                         "heuristic": "question_mc_singleselect_scale",
                         "rating": "question_mc_singleselect_scale",
                         "pre_test": "question"}


def get_questions():
    with open(os.path.join(DATA_ROOT, "questions.csv")) as questions_csv:
        question_reader = csv.DictReader(questions_csv)
        for row in question_reader:
            # Convert from 0 indexed to 1 indexed
            dataset_id = int(row["dataset_id"]) + 1
            dataset = Dataset.query.get(dataset_id)

            includes_explanation = int(random.random() * 10) % 2
            needs_reflection = int(random.random() * 10) % 2

            if not dataset:
                dataset = Dataset(id=dataset_id)
                db.session.add(dataset)

            explanation = ""
            if includes_explanation:
                explanation = "This explains question " + \
                str(row["question_id"])

            question = Question(
                id=row["question_id"],
                datasets=[dataset],
                question=row["question_text"],
                type=question_type_mapping[row["question_type"]],
                explanation=explanation,
                needs_reflection=needs_reflection)


            if "scale" in question.type:
                for i in range(0, 5):
                    question.choices.append(Choice(choice=str(i), label=str(i),
                                                   correct=True))

            db.session.add(question)
    db.session.commit()

def get_choices():
    with open(os.path.join(DATA_ROOT, "choices.csv")) as choices_csv:
        choice_reader = csv.DictReader(choices_csv)
        for row in choice_reader:
            choice = Choice(
                question_id=row["question_id"],
                choice=row["answer_text"],
                correct=row["correct"] == "yes",
                label=row["answer_letter"])
            db.session.add(choice)
    with open(os.path.join(DATA_ROOT, 'graph_table.csv')) as graphs_csv:
        graphs = csv.DictReader(graphs_csv)

        for graph in graphs:
            graph = Graph(
                id=graph["graph_id"],
                dataset_id=int(graph["dataset"])+1,
                filename=graph["graph_location"])
            db.session.add(graph)
    db.session.commit()

# In this list, each list is associated with a participant (one to one).  The
# first three tuples in each list are associated with training questions.  The
# last three tuples in each list are associated with pre/post questions.  In
# each tuple, the first number represents the dataset of the question.  The
# second number is associated with the ID of the graph. TODO: simplify this
# relationship.  The order of the tuples along with the participant id gives
# the participant test id.  Note: No participant has two tuples with the same
# dataset - this means the relationship between participant test and dataset is
# many to one.

participant_question_list = \
[[(1, 2), (3, 2), (4, 0), (2, 1), (5, 0), (0, 0)],
 [(1, 2), (0, 2), (5, 1), (2, 0), (3, 0), (4, 1)],
 [(3, 0), (2, 1), (4, 0), (5, 1), (0, 0), (1, 2)],
 [(5, 2), (2, 2), (0, 1), (1, 0), (3, 1), (4, 0)],
 [(2, 2), (0, 1), (3, 1), (4, 0), (1, 1), (5, 1)],
 [(0, 0), (3, 0), (1, 0), (2, 2), (5, 2), (4, 2)],
 [(4, 2), (1, 1), (5, 2), (0, 0), (3, 1), (2, 1)],
 [(4, 2), (3, 0), (1, 2), (0, 1), (5, 2), (2, 1)],
 [(3, 1), (2, 0), (4, 2), (1, 1), (0, 1), (5, 2)],
 [(0, 2), (4, 1), (3, 0), (5, 0), (1, 1), (2, 0)],
 [(5, 1), (4, 1), (0, 2), (3, 2), (1, 2), (2, 0)],
 [(2, 1), (5, 0), (0, 2), (3, 2), (4, 2), (1, 1)],
 [(3, 1), (5, 2), (4, 1), (0, 2), (2, 0), (1, 0)],
 [(1, 1), (5, 1), (2, 2), (4, 0), (3, 1), (0, 2)],
 [(2, 0), (1, 0), (5, 0), (4, 1), (0, 2), (3, 2)],
 [(1, 1), (5, 1), (0, 2), (4, 2), (2, 1), (3, 1)],
 [(5, 1), (4, 2), (2, 0), (1, 2), (3, 2), (0, 1)],
 [(0, 0), (2, 2), (1, 0), (4, 1), (5, 2), (3, 2)],
 [(0, 1), (1, 2), (5, 2), (2, 0), (4, 2), (3, 0)],
 [(1, 0), (3, 2), (0, 0), (2, 2), (4, 0), (5, 0)],
 [(3, 2), (2, 1), (4, 1), (1, 0), (5, 1), (0, 0)],
 [(1, 0), (3, 2), (5, 0), (0, 1), (4, 1), (2, 2)],
 [(5, 2), (3, 1), (1, 1), (0, 0), (4, 0), (2, 2)],
 [(4, 1), (0, 0), (3, 1), (2, 1), (5, 1), (1, 0)],
 [(5, 0), (2, 0), (0, 1), (3, 0), (1, 1), (4, 2)],
 [(0, 2), (4, 0), (1, 1), (3, 1), (2, 2), (5, 0)],
 [(2, 0), (0, 0), (3, 0), (1, 2), (5, 0), (4, 1)],
 [(0, 1), (4, 2), (2, 1), (5, 2), (1, 0), (3, 0)],
 [(5, 0), (4, 0), (2, 2), (3, 0), (1, 2), (0, 1)],
 [(4, 0), (1, 2), (2, 1), (5, 1), (0, 2), (3, 2)]]

def get_students():
    combined_id_list = []
    question_participant_id_list = []
    heuristic_participant_id_list = []
    experiments = Experiment.query.all()

    participant_role = Role(name="participant", description="Participant role")
    experimenter_role = Role(name="experimenter", description="Experimenter role")

    with open(os.path.join(DATA_ROOT, "participant_id_list.csv")) as participants_csv:
        participant_reader = csv.DictReader(participants_csv)
        for row in participant_reader:
            questions_id = row["Questions"]
            heuristics_id = row["Heuristics"]
            if questions_id:
                question_participant_id_list.append(questions_id)
                combined_id_list.append(questions_id)
            if heuristics_id:
                heuristic_participant_id_list.append(heuristics_id)
                combined_id_list.append(heuristics_id)

    for pid in combined_id_list:
        participant = Participant(
            id=pid,
            email=str(pid),
            password=str(pid),
            opt_in=False,
            progress="pre_test",
            active=True,
            roles=[participant_role]
        )
        for exp in experiments:
            part_exp = ParticipantExperiment(
                progress=0,
                participant_id=pid,
                experiment_id=exp.id)
            db.session.add(part_exp)
        db.session.add(participant)

    root = User(
        email="experimenter@example.com",
        password="foobar",
        active=True,
        roles=[experimenter_role]
    )

    db.session.commit()
    return question_participant_id_list, heuristic_participant_id_list

def create_participant_data(pid_list, participant_question_list, test, group):
    """
    sid_list: list of participant id's
    participant_question_list: magic list of lists of tuples
    test: pre_test or training or post_test
    group: question or heuristic
    """
    experiments = {"pre_test":
                   Experiment.query.filter_by(name="pre_test").one(),
                   "test": Experiment.query.filter_by(name="test").one(),
                   "post_test": Experiment.query.filter_by(name="post_test").one()}
    missing_qs = set()
    if test == 'pre_test' or test == 'post_test':
        question_list = [x[:3] for x in participant_question_list]
    else:
        #pick last three
        question_list = [x[3:] for x in participant_question_list]
    for n, participant in enumerate(question_list):
        #n is the nth participant
        participant_id = pid_list[n]
        participant_experiment = ParticipantExperiment.query.\
                filter_by(participant_id=participant_id).\
                filter_by(experiment_id=experiments[test].id).one()
        #count the order for each participant per test
        order = 0
        for ix, graph in enumerate(participant):
            participant_test_id = int(str(participant_id)+str(ix))
            dataset = graph[0]
            graph_id = int(str(dataset)+str(graph[1]+1))
            if test == 'pre_test' or test == 'post_test':
                order += 1
                #TODO: why +5
                question_id = int(str(dataset)+str(5))

                if not Question.query.get(question_id):
                    missing_qs.add(question_id)
                    continue

                #write row to db
                assignment = Assignment(
                    participant_id=participant_id,
                    activity_id=question_id,
                    experiment_id=experiments[test].id,
                    participant_experiment_id=participant_experiment.id,
                    graphs=[Graph.query.get(graph_id)])

                db.session.add(assignment)

            else: #training
                if group == 'heuristic':
                    #three questions per dataset, three datasets, so 9 questions
                    # for the training part
                    for x in range(6, 9):
                        order += 1
                        question_id = int(str(dataset)+str(x))

                        if not Question.query.get(question_id):
                            missing_qs.add(question_id)
                            continue

                        #write row to db
                        assignment = Assignment(
                            participant_id=participant_id,
                            activity_id=question_id,
                            experiment_id=experiments[test].id,
                            participant_experiment_id=participant_experiment.id,
                            graphs=[Graph.query.get(graph_id)])

                        db.session.add(assignment)
                else:
                    #multiple choice questions
                    for x in range(3):
                        order += 1
                        question_id = int(str(dataset)+str(x + 1))
                        #write row to db
                        if not Question.query.get(question_id):
                            missing_qs.add(question_id)
                            continue
                        assignment = Assignment(
                            participant_id=participant_id,
                            activity_id=question_id,
                            experiment_id=experiments[test].id,
                            participant_experiment_id=participant_experiment.id,
                            graphs=[Graph.query.get(graph_id)])

                        db.session.add(assignment)

                #only have rating question for training
                order += 1
                question_id = int(str(dataset)+str(4))
                #write row to db
                if not Question.query.get(question_id):
                    missing_qs.add(question_id)
                    continue

                assignment = Assignment(
                    participant_id=participant_id,
                    activity_id=question_id,
                    experiment_id=experiments[test].id,
                    participant_experiment_id=participant_experiment.id,
                    graphs=[Graph.query.get(graph_id)])

                db.session.add(assignment)

    db.session.commit()
    print "Completed storing {} {} tests".format(test, group)
    if missing_qs:
        print "Failed to find the following questions:"
        print missing_qs

#create all the participant_test table data

def create_assignments(participants_question, participants_heuristic):
    for test in ['pre_test', 'test', 'post_test']:
        create_participant_data(participants_question,
                                participant_question_list, test, 'question')
        create_participant_data(participants_heuristic,
                                participant_question_list, test, 'heuristic')

if __name__ == "__main__":
    with app.app_context():
        clear_db()
        get_experiments()
        get_questions()
        get_choices()
        questions, heuristics = get_students()
        create_assignments(questions, heuristics)
