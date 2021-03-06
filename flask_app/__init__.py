import logging
import os
from flask import Flask, render_template, request, flash
from flask import session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_pagedown import PageDown
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, IntegerField, DecimalField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange
import sqlalchemy
import flask_app.gcp.languageapi as nlp
import googleapiclient.discovery

db_user = os.environ.get("DB_USER")
db_pass = os.environ.get("DB_PASS")
db_name = os.environ.get("DB_NAME")
cloud_sql_connection_name = os.environ.get("CLOUD_SQL_CONNECTION_NAME")
CLOUD_STORAGE_BUCKET = os.environ.get('CLOUD_STORAGE_BUCKET')



def predict_json(project, model, instances, version=None):
    """Send json data to a deployed model for prediction.
    Args:
        project (str): project where the AI Platform Prediction Model is deployed.
        model (str): model name.
        instances ([[float]]): List of input instances, where each input
        instance is a list of floats.
        version: str, version of the model to target.
    Returns:
        Mapping[str: any]: dictionary of prediction results defined by the
            model.
    """
    # Create the AI Platform Prediction service object.
    # To authenticate set the environment variable
    # GOOGLE_APPLICATION_CREDENTIALS=<path_to_service_account_file>
    service = googleapiclient.discovery.build('ml', 'v1')
    name = 'projects/{}/models/{}'.format(project, model)

    if version is not None:
        name += '/versions/{}'.format(version)

    response = service.projects().predict(
        name=name,
        body={'instances': instances}
    ).execute()

    if 'error' in response:
        raise RuntimeError(response['error'])

    return response['predictions']


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
    emp = SelectField(
        u'How many years have you been with your employer?',
        choices=[('1', '<1 year'), ('2', '1 year'), ('3', '2 years'), ('4', '3 years'),
                 ('5', '4 years'), ('6', '5 years'), ('7', '6 years'), ('8', '7 years'),
                 ('9', '8 years'), ('10', '9 years'), ('11', '10 years+')],
        validators=[DataRequired()])
    home = SelectField(
        u'What is your housing status? (1-Rent, 2-Other, 3-Mortgage, 4-Own)',
        choices=[('1', 'Rent'), ('4', 'Own'), ('3', 'Mortgage'), ('2', 'Other')],
        validators=[DataRequired()])
    zipcode = IntegerField(
        u'What are the first 3 digits of your zip code?',
        validators=[DataRequired()])
    acc = IntegerField(
        u'How many accounts have you ever had in your name?',
        validators=[DataRequired()])
    inc = IntegerField(
        u'What is your annual income? (no commas)',
        validators=[DataRequired()])
    ratio = DecimalField(
        u'What is your debt-to-income ratio? (round to 2 decimals)',
        validators=[DataRequired()])
    descr_input = StringField(
        u'Why do you need this loan? (enter text)',
        validators=[DataRequired(), Length(max=200)])
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():
    # Set form
    form = ApplicationForm(request.form)
    # Set prediction
    pred = None
    # Form submission
    if request.method == 'POST' and form.validate_on_submit():
        # Receive values from form and set the form value to '' for session
        emp_length_cat = (request.form.get('emp'))
        home_status = (request.form.get('home'))
        zip3 = (request.form.get('zipcode'))
        total_acc = (request.form.get('acc'))
        annual_inc = (request.form.get('inc'))
        dti = (request.form.get('ratio'))
        descr = (request.form.get('descr_input'))
        scores = nlp.analyze(descr)
        scores = round(scores, 2)
        # Put features into format the model can receive
        instances = [[emp_length_cat, home_status, zip3,
                     total_acc, annual_inc, dti, scores]]
        # Create prediction
        pred_list = predict_json('lending-274219', 'clf', instances, version='v9')
        pred = pred_list[0]
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
                        scores,
                        predict)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s, %s)""",
                (emp_length_cat, home_status, zip3,
                 total_acc, annual_inc, dti, descr, scores, pred)
            )
        if pred == 1:
            flash('Our model has predicted you will default, therefore your loan application has been DENIED.', 'danger')
        elif pred == 0:
            flash('Our model has predicted you will not default, congratulations you have been APPROVED.', 'info')
        else:
            flash('A credit default prediction was not created. Contact support.')
        return redirect(url_for('index'))
    return render_template('index.html',
                           form=form
                           )


@app.route('/info', methods=['GET', 'POST'])
def info():
    return render_template('info.html')


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500
