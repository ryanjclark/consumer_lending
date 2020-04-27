import logging
from flask import Flask
from flask import jsonify

app = Flask(__name__, static_folder='static')


@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return 'Hello World! This main.py is located within ./main.py'


@app.route('/sentiment/<desc>')
def sentiment(desc):
    desc_json = {"description": desc}
    return jsonify(desc_json)


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


# """
# Register blueprints for api and quiz
# """
# from flaskapp import api
# from flaskapp import webapp
# from flaskapp.api.routes import api_blueprint
# from flaskapp.webapp.routes import webapp_blueprint


# app.register_blueprint(api.routes.api_blueprint, url_prefix='/api')
# app.register_blueprint(webapp.routes.webapp_blueprint, url_prefix='')