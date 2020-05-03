import logging
import os
import datetime
from flask import Flask, render_template, request
from flask import jsonify, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_pagedown import PageDown
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import sqlalchemy
import flask_app.gcp.languageapi as nlp


db_user = os.environ.get("DB_USER")
db_pass = os.environ.get("DB_PASS")
db_name = os.environ.get("DB_NAME")
cloud_sql_connection_name = os.environ.get("CLOUD_SQL_CONNECTION_NAME")
CLOUD_STORAGE_BUCKET = os.environ.get('CLOUD_STORAGE_BUCKET')

# Instantiate app
app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'root'

# Instantiate flask modules
bootstrap = Bootstrap(app)
moment = Moment(app)
pagedown = PageDown(app)
logger = logging.getLogger()

# Use SQLAlchemy to create CloudSQL connection
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
    pool_size=5,
    max_overflow=2,
    pool_timeout=30,
    pool_recycle=1800,
)


# Form to receive applicant loan request
class DescrForm(FlaskForm):
    descr = StringField(
        'Why do you need this loan today?',
        validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = DescrForm()
    data = []
    with db.connect() as conn:
        recent_data = conn.execute(
            "SELECT loan_amnt, settlement_date FROM loans " "ORDER BY settlement_date DESC LIMIT 5"
        ).fetchall()
        for row in recent_data:
            data.append({"loan_amnt": row[0], "settlement_date": row[1]})
    if request.method == 'POST' and form.validate():
        description = form.descr.data
        form.descr.data = ''
        session['score'] = nlp.analyze(description)
        return redirect(url_for('index'))
    return render_template('index.html',
                           form=form,
                           recent_data=data,
                           score=session.get('score'))


# Alternate route for NLP API sentiment
@app.route('/form')
def index_form():
    return """
<form method="POST" action="/analyze" enctype="multipart/form-data">
    <input type="text" name="description">
    <input type="submit">
</form>
"""


@app.route('/analyze', methods=['POST'])
def score_nlp():
    description = request.form['description']
    score = nlp.analyze(description)
    score_int = str(score)
    return score_int


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500
