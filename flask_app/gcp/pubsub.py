import json
import logging
import os
from google.cloud import pubsub_v1
from flask import current_app

project_id = os.getenv('GCLOUD_PROJECT')

publisher = pubsub_v1.PublisherClient()
sub_client = pubsub_v1.SubscriberClient()
topic_path = publisher.topic_path(project_id, 'lending-descr')
sub_path = sub_client.subscription_path(project_id, 'worker-subscription')

"""
Publishes feedback info
- jsonify feedback object
- encode as bytestring
- publish message
- return result
"""


def publish_feedback(feedback):
    payload = json.dumps(feedback, indent=2, sort_keys=True)
    data = payload.encode('utf-8')
    future = publisher.publish(topic_path, data=data)
    return future.result()


"""pull_feedback
Starts pulling messages from subscription
- receive callback function from calling module
- initiate the pull providing the callback function
"""


def pull_feedback(callback):
    sub_client.subscribe(sub_path, callback=callback)
