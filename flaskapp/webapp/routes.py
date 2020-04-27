"""
Set up Flask stuff
"""
from flask import Blueprint, render_template
from flask import send_from_directory
from flask import request, redirect

from flaskapp.webapp import questions

"""
configure blueprint
"""
webapp_blueprint = Blueprint(
    'webapp',
    __name__,
    template_folder='templates',
)


"""
Renders home page
"""
@webapp_blueprint.route('/')
def serve_home():
    return render_template('home.html')

"""
Serves static file with angular client app
"""
@webapp_blueprint.route('/client/')
def serve_client():
    return send_from_directory('webapp/static/client', 'index.html')

"""
Serves static files used by angular client app
"""
@webapp_blueprint.route('/client/<path:path>')
def serve_client_files(path):
    return send_from_directory('webapp/static/client', path)

"""
Handles definition and storage of new questions
- GET method shows question entry form
- POST method save question
"""
@webapp_blueprint.route('/questions/add', methods=['GET', 'POST'])
def add_question():
    if request.method == 'GET':
        return render_template('add.html', question={}, action='Add')
    elif request.method == 'POST':
        data = request.form.to_dict(flat=True)
        image_file = request.files.get('image')
        questions.save_question(data, image_file)
        return redirect('/', code=302)
    else:
        return "Method not supported for /questions/add"