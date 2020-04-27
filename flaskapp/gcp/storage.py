import os
from google.cloud import storage

project_id = os.getenv('GCLOUD_PROJECT')
bucket_name = os.getenv('GCLOUD_BUCKET')
storage_client = storage.Client()
bucket = storage_client.get_bucket(bucket_name)
# lending-274219.appspot.com bucket name?

"""
Uploads a file to a given Cloud Storage bucket and returns the public url
to the new object.
"""
def upload_file(image_file, public):

    # TODO: Use the bucket to get a blob object

    blob = bucket.blob(image_file.filename)

    # TODO: Use the blob to upload the file

    blob.upload_from_string(
        image_file.read(),
        content_type=image_file.content_type)

    # TODO: Make the object public

    if public:
        blob.make_public()

    # TODO: Modify to return the blob's Public URL

    return blob.public_url

    # END TODO