"""
Setup flask
"""
from flask import Flask
app = Flask(__name__, static_folder='static')

"""
Register blueprints for api and quiz
"""
from flaskapp import api
from flaskapp import webapp
from flaskapp.api.routes import api_blueprint
from flaskapp.webapp.routes import webapp_blueprint


app.register_blueprint(api.routes.api_blueprint, url_prefix='/api')
app.register_blueprint(webapp.routes.webapp_blueprint, url_prefix='')