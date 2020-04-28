import os
project_id = os.getenv('GCLOUD_PROJECT')

from flask import current_app
from google.cloud import datastore

datastore_client = datastore.Client(project_id)