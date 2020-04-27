from flaskapp.gcp import storage, datastore

"""
uploads file into google cloud storage
- upload file
- return public_url
"""
def upload_file(image_file, public):
    if not image_file:
        return None

    public_url = storage.upload_file(
       image_file,
       public
    )

    return public_url

"""
uploads file into google cloud storage
- call method to upload file (public=true)
- call datastore helper method to save question
"""
def save_question(data, image_file):
    if image_file:
        data['imageUrl'] = unicode(upload_file(image_file, True))
    else:
        data['imageUrl'] = u''
    data['correctAnswer'] = int(data['correctAnswer'])
    datastore.save_question(data)
    return