import json
from flask import Response
from flaskapp.gcp import datastore, pubsub

"""
Gets list of questions from datastore
- Create query
- Filter on quiz
- Call the datastore helper to get back JSON
- Pretty print JSON
- Set header and return the response
"""
def get_questions(quiz_name):
    questions = datastore.list_entities(quiz_name)
    payload = {'questions': list(questions)}
    payload = json.dumps(payload, indent=2, sort_keys=True)
    response = Response(payload)
    response.headers['Content-Type'] = 'application/json'
    return response

"""
Grades submitted answers
- Get list of questions with correct answers from datastore
- Iterate through questions, find any submitted answers that match
- Count total number of questions for which there is >0 correct answers
- Compose and pretty print payload
- Compose and return response
"""
def get_grade(quiz_name, answers):
    questions = datastore.list_entities(quiz_name, False)
    score = len(list(filter(lambda x: x > 0,
                    list(map(lambda q:
                         len(list(filter(lambda answer:
                            answer['id'] == q['id'] and
                            int(answer['answer']) == q['correctAnswer'],
                            answers)))
                         , questions))
                )))
    payload = {'correct': score, 'total': len(questions)}
    payload = json.dumps(payload, indent=2, sort_keys=True)
    response = Response(payload)
    response.headers['Content-Type'] = 'application/json'
    return response

"""
Publish feedback
- Call pubsub helper
- Compose and return response
"""
def publish_feedback(feedback):
    # TODO: Publish the feedback using your pubsub module, return the result

    result = pubsub.publish_feedback(feedback)
    response = Response(json.dumps(result, indent=2, sort_keys=True))
    response.headers['Content-Type'] = 'application/json'
    return response

    # END TODO
