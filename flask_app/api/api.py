import json
from flask import Response
from flask_app.gcp import datastore, pubsub

def publish_feedback(feedback):
    result = pubsub.publish_feedback(feedback)
    response = Response(json.dumps(result, indent=2, sort_keys=True))
    response.headers['Content-Type'] = 'application/json'
    return response
