import logging
import os
from flask import Flask, render_template, request, flash
from flask import session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_pagedown import PageDown
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
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
    'mysql+pymysql://root:root@/loan_db?unix_socket=/cloudsql/lending-274219:us-central1:loan-data',
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


class ApplicationForm(FlaskForm):
    emp = IntegerField(
        u'How long have you been with your employer? (1-11)',
        validators=[DataRequired()])
    home = IntegerField(
        u'What is your housing status? (1-Rent, 2-Other, 3-Mortgage, 4-Own)',
        validators=[DataRequired()])
    zipcode = IntegerField(
        u'What is the first 3 digits of your zip code?',
        validators=[DataRequired()])
    acc = IntegerField(
        u'How many accounts have you ever had in your name?',
        validators=[DataRequired()])
    inc = IntegerField(
        u'What is your annual income? (no commas)',
        validators=[DataRequired()])
    ratio = IntegerField(
        u'What is your debt-to-income ratio? (round to 2 decimals)',
        validators=[DataRequired()])
    descr_input = StringField(
        u'Why do you need this loan? (enter text)',
        validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():
    # Set form
    form = ApplicationForm(request.form)
    # Form submission
    if request.method == 'POST' and form.validate_on_submit():
        # Receive values from form and set the form value to '' for next session
        emp_length_cat = (request.form.get('emp'))
        home_status = (request.form.get('home'))
        zip3 = (request.form.get('zipcode'))
        total_acc = (request.form.get('acc'))
        annual_inc = (request.form.get('inc'))
        dti = (request.form.get('ratio'))
        descr = (request.form.get('descr_input'))
        scores = nlp.analyze(descr)
        with db.connect() as conn:
            conn.execute(
                """INSERT INTO
                    loans_tbl (
                        emp_length_cat,
                        home_status,
                        zip3,
                        total_acc,
                        annual_inc,
                        dti,
                        descr,
                        scores)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                (emp_length_cat, home_status, zip3,
                 total_acc, annual_inc, dti, descr, scores)
            )
        flash('Thanks for applying')
        return redirect(url_for('index'))
    return render_template('index.html',
                           form=form,
                           )


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500
