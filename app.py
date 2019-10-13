from flask import ( 
    Flask, request, jsonify, send_from_directory , g,
    session as login_session)
from flask_httpauth import HTTPBasicAuth
from models import *
import re


# setup authentication object
auth = HTTPBasicAuth()


# Authenticate credentials @auth.login_required
@auth.verify_password
def authenticate(username_or_token, password):
    """
    authentication based on one of two styles:
    username:password OR token:'blank'
    """
    # skip authentication and allow the following requests for public
    if (
      request.method == 'GET' and
      (
        bool(re.search(r'/survey', request.path))
      )
    ): return True
    # verify both fields exist
    if not (username_or_token and password): return False
    # try token based authentication
    user_id = User.verify_auth_token(username_or_token)
    if user_id:
        user = User.query.filter_by(id=user_id).first()
    # try username:password authentication
    else:
        users = User.query.filter_by(username=username_or_token).all()
        # check invalid username
        if not users: return False
        user = users[0]
        # check invalid password
        if not user.verify_password(password): return False
    # add user to g object for further use
    g.user = user
    return True


# Register new user
@app.route('/register', methods=['POST'])
def register():
    # check request is JSON
    if not request.is_json:
        return jsonify('You have to send a valid JSON')
    # get credentials
    data = request.json
    username = data.get('username')
    password = data.get('password')
    # validate them
    if not (username and password):
        return jsonify({'error': 'missing username or password'})
    # check if user exists
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({'error': 'this username already exists'})
    # add new user
    new_user = User()
    new_user.username = username
    new_user.hash_password(password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'success': 'You have registered successfully'})


# Get authentication token
@app.route('/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


# Homepage
@app.route('/')
def index():
    return "Hello World!"


# GET surveys or POST new survey
@app.route('/survey', methods=['GET', 'POST'])
@auth.login_required
def survey():
    if request.method == 'POST':
        # validate data 
        request_errors = validate_request(request)
        if request_errors:
            return jsonify({'errors': request_errors})
        # get data
        survey_data = request.json
        # create new survey
        new_survey = Survey()
        new_survey.name = survey_data.get('name')
        new_survey.description = survey_data.get('description')
        new_survey.start_date = survey_data.get('start_date')
        new_survey.end_date = survey_data.get('end_date')
        new_survey.user = g.user
        db.session.add(new_survey)
        # add survey questions
        for question in survey_data.get('questions'):
            survey_question = Question()
            survey_question.body = question.get('question').get('body')
            survey_question.note = question.get('question').get('note')
            survey_question.survey = new_survey
            db.session.add(survey_question)
        # save to DB
        db.session.commit()
        return jsonify({'success': 'Your survey was successfully added to the database.'})
    
    else:
        # get surveys data in a serialized format
        surveys = [survey.serialize for survey in Survey.query.all()]
        return jsonify(surveys)


def validate_request(request):
    """
    validate request data sent to '/survey' via 'post' before adding new survey to DB.
    """
    errors = []
    # check request is JSON
    if not request.is_json:
        errors.append('You have to send a valid JSON')
        return errors
    else:
        survey_data = request.json
    # check name is provided
    name = survey_data.get('name')
    if not name:
        errors.append('You must provide a survey name')
    # check start_date is provided and in correct format
    start_date = survey_data.get('start_date')
    if not start_date:
        errors.append('You must provide a start_date')
    else:
        try:
            datetime.strptime(start_date, '%d/%m/%Y %H:%M')
        except ValueError:
            errors.append('Incorrect start_date format, should be (dd/mm/yyyy HH:MM)')
    # check end_date is in correct format if provided
    end_date = survey_data.get('end_date')
    if end_date:
        try:
            datetime.strptime(end_date, '%d/%m/%Y %H:%M')
        except ValueError:
            errors.append('Incorrect end_date format, should be (dd/mm/yyyy HH:MM)')
    # check there is at least one question with a body
    questions = survey_data.get('questions')
    if not questions:
        errors.append('You must provide at least one question')
    else:
        for question in questions:
            body = question.get('question').get('body')
            if not body:
                errors.append('You must provide a question body')
    
    return errors


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
