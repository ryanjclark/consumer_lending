import logging
import os
import datetime
from flask import Flask, render_template, request, Response, Request
from flask import jsonify
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_pagedown import PageDown
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import sqlalchemy
from google.cloud import storage
import flask_app.gcp.languageapi



db_user = os.environ.get("DB_USER")
db_pass = os.environ.get("DB_PASS")
db_name = os.environ.get("DB_NAME")
cloud_sql_connection_name = os.environ.get("CLOUD_SQL_CONNECTION_NAME")
CLOUD_STORAGE_BUCKET = os.environ.get('CLOUD_STORAGE_BUCKET')

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'root'

bootstrap = Bootstrap(app)
moment = Moment(app)
pagedown = PageDown(app)

logger = logging.getLogger()

db = sqlalchemy.create_engine(
    'mysql+pymysql://root:root@/lending-club-db?unix_socket=/cloudsql/lending-274219:us-central1:lending-storage',
    # sqlalchemy.engine.url.URL(
    #     drivername="mysql+pymysql",
    #     username=db_user,
    #     password=db_pass,
    #     database=db_name,
    #     query={"unix_socket": "/cloudsql/{}".format(cloud_sql_connection_name)}
    # )
    # ),
    # ... Specify additional properties here.
    # [START_EXCLUDE]
    # [START cloud_sql_mysql_sqlalchemy_limit]
    # Pool size is the maximum number of permanent connections to keep.
    pool_size=5,
    # Temporarily exceeds the set pool_size if no connections are available.
    max_overflow=2,
    # The total number of concurrent connections for your application will be
    # a total of pool_size and max_overflow.
    # [END cloud_sql_mysql_sqlalchemy_limit]
    # [START cloud_sql_mysql_sqlalchemy_backoff]
    # SQLAlchemy automatically uses delays between failed connection attempts,
    # but provides no arguments for configuration.
    # [END cloud_sql_mysql_sqlalchemy_backoff]
    # [START cloud_sql_mysql_sqlalchemy_timeout]
    # 'pool_timeout' is the maximum number of seconds to wait when retrieving a
    # new connection from the pool. After the specified amount of time, an
    # exception will be thrown.
    pool_timeout=30,  # 30 seconds
    # [END cloud_sql_mysql_sqlalchemy_timeout]
    # [START cloud_sql_mysql_sqlalchemy_lifetime]
    # 'pool_recycle' is the maximum number of seconds a connection can persist.
    # Connections that live longer than the specified amount of time will be
    # reestablished
    pool_recycle=1800,  # 30 minutes
    # [END cloud_sql_mysql_sqlalchemy_lifetime]
    # [END_EXCLUDE]
)


class NameForm(FlaskForm):
    name = StringField(
        'Send applicant free-form description for sentiment score',
        validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    data = []
    with db.connect() as conn:
        # Execute the query and fetch all results
        recent_data = conn.execute(
            "SELECT loan_amnt, settlement_date FROM loans " "ORDER BY settlement_date DESC LIMIT 5"
        ).fetchall()
        # Convert the results into a list of dicts representing votes
        for row in recent_data:
            data.append({"loan_amnt": row[0], "settlement_date": row[1]})
    return render_template('index.html', form=form, recent_data=data)


@app.route('/sentiment/<desc>')
def sentiment(desc):
    desc_json = {"description": desc}
    return jsonify(desc_json)


@app.route('/form')
def index_form():
    return """
<form method="POST" action="/analyze" enctype="multipart/form-data">
    <input type="text" name="description">
    <input type="submit">
</form>
"""


@app.route('/analyze', methods=['POST'])
def upload():
    """Process the uploaded file and upload it to Google Cloud Storage."""
    # uploaded_file = request.text.get('description')

    # if not uploaded_file:
    #     return 'No file uploaded.', 400

    # Create a Cloud Storage client.
    # gcs = storage.Client()

    # Get the bucket that the file will be uploaded to.
    # bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)

    # # Create a new blob and upload the file's content.
    # blob = bucket.blob(uploaded_file.filename)

    # blob.upload_from_string(
    #     uploaded_file.read(),
    #     content_type=uploaded_file.content_type
    # )

    # The public URL can be used to directly access the uploaded file via HTTP.
    # return blob.public_url
    description = request.form['description']
    score = flask_app.gcp.languageapi.analyze(description)
    score_int = str(score)
    return score_int

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