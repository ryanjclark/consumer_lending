import logging
import sys
import time
import json
from flask_app.gcp import pubsub, languageapi

"""
Configure logging
"""
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
log = logging.getLogger()

"""
Receives pulled messages, analyzes and stores them
- Acknowledge the message
- Log receipt and contents
- convert json string
- call helper module to do sentiment analysis
- log sentiment score
- call helper module to persist to spanner
- log feedback saved
"""


def pubsub_callback(message):
    message.ack()
    log.info('Message received')
    log.info(message)
    data = json.loads(message.data)
    score = languageapi.analyze(str(data['lending-descr']))
    log.info('Score: {}'.format(score))
    data['score'] = score
    # datastore.save_feedback(data)
    # log.info('Feedback saved')


"""
Pulls messages and loops forever while waiting
- initiate pull 
- loop once a minute, forever
"""


def main():
    log.info('Worker starting...')
    pubsub.pull_feedback(pubsub_callback)
    while True:
        time.sleep(60)


if __name__ == '__main__':
    main()
