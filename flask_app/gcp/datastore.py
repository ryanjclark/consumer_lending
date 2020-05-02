import re
from google.cloud import datastore

"""
Get datastore management objects
"""

# TODO: Create a spanner Client

datastore_client = datastore.Client()

# END TODO


# TODO: Get a reference to the Cloud Spanner quiz-instance

# instance = datastore_client.instance('quiz-instance')

# END TODO

# TODO: Get a referent to the Cloud Spanner quiz-database

# database = instance.database('quiz-database')

# END TODO

"""
Takes an email address and reverses it (to be used as primary key)
"""
def reverse_email(email):
    return '_'.join(list(reversed(email.replace('@','_').
                        replace('.','_').
                        split('_'))))

"""
Persists feedback data into Spanner
- create primary key value
- do a batch insert (even though it's a single record)
"""
def save_feedback(data):
    # TODO: Create a batch object for database operations

    with database.batch() as batch:
        # TODO: Create a key for the record
        # from the email, quiz and timestamp

        feedback_id = '{}_{}_{}'.format(reverse_email(data['email']),
                                        data['quiz'],
                                        data['timestamp'])

        # END TODO

        # TODO: Use the batch to insert a record
        # into the feedback table
        # This needs the columns and values

        batch.insert(
            table='feedback',
            columns=(
                'feedbackId',
                'email',
                'quiz',
                'timestamp',
                'rating',
                'score',
                'feedback'
            ),
            values=[
                (
                    feedback_id,
                    data['email'],
                    data['quiz'],
                    data['timestamp'],
                    data['rating'],
                    data['score'],
                    data['feedback']
                )
            ]
        )

        # END TODO

    # END TODO