"""Post a HIT to the amazon mturk servers.

This script is adapted from akuznets0v/quickstart-mturk.
"""

import yaml
from boto.mturk.connection import MTurkConnection
from boto.mturk.question import ExternalQuestion
from boto.mturk.qualification import Qualifications
from boto.mturk.price import Price

# Config variables
DEV_ENVIROMENT_BOOLEAN = True
"""bool: if True, then post the HIT to the mturk sandbox. Otherwise, post to
the live site.
"""

REWARD_AMOUNT = 0
"""float: The dollar amount to give turkers for completing the HIT.
"""

EXPERIMENT_ID = 0
"""int: ID of the experiment you wish to post.
"""

def main():
    """Post a HIT to amazon.
    """
    with open("instance/mturk.yaml") as f:
        config = yaml.load(f)

    # This allows us to specify whether we are pushing to the sandbox or live
    # site.
    if DEV_ENVIROMENT_BOOLEAN:
        AMAZON_HOST = "mechanicalturk.sandbox.amazonaws.com"
    else:
        AMAZON_HOST = "mechanicalturk.amazonaws.com"

    connection = MTurkConnection(
        aws_access_key_id=config["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=config["AWS_SECRET_ACCESS_KEY"],
        host=AMAZON_HOST)

    # frame_height in pixels
    frame_height = 800

    # Here, I create two sample qualifications
    qualifications = Qualifications()
    # qualifications.add(PercentAssignmentsApprovedRequirement(
    # comparator="GreaterThan", integer_value="90"))
    # qualifications.add(NumberHitsApprovedRequirement(
    # comparator="GreaterThan", integer_value="100"))

    # This url will be the url of your application, with appropriate GET
    # parameters

    url = ("https://104.236.112.220/mturk/register?"
           "experiment_id={}").format(EXPERIMENT_ID)
    questionform = ExternalQuestion(url, frame_height)
    create_hit_result = connection.create_hit(
        title="Insert the title of your HIT",
        description="Insert your description here",
        keywords=["add", "some", "keywords"],
        # duration is in seconds
        duration=60 * 60,
        # max_assignments will set the amount of independent copies of the task
        # (turkers can only see one)
        max_assignments=15,
        question=questionform,
        reward=Price(amount=REWARD_AMOUNT),
        # Determines information returned by method in API, not super important
        response_groups=('Minimal', 'HITDetail'),
        qualifications=qualifications,
    )
    print "HIT Created."
    print "ID: {}".format(create_hit_result[0].HITId)

if __name__ == "__main__":
    main()
