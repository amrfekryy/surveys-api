from flask import ( 
    Flask, request, jsonify, send_from_directory )

from models import *
# from flask_swagger_ui import get_swaggerui_blueprint


# ### swagger specific ###
# @app.route('/static/<path:path>')
# def send_static(path):
#     return send_from_directory('static', path)

# SWAGGER_URL = '/swagger'
# API_URL = '/static/swagger.json'
# SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
#     SWAGGER_URL,
#     API_URL,
# )
# app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
# ### end swagger specific ###


@app.route('/')
def index():
    return """
    Hi, you are at the index page. Go to '/survey' to test the API.
    """


@app.route('/survey', methods=['GET', 'POST'])
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
        db.session.add(new_survey)

        # add survey questions
        for question in survey_data.get('questions'):
            survey_question = Question()
            survey_question.body = question.get('question').get('body')
            survey_question.note = question.get('question').get('note')
            survey_question.survey = new_survey
            db.session.add(survey_question)
        
        db.session.commit()

        return jsonify({'success': 'Your survey was successfully added to the database.'})
    
    else:
        # surveys = Survey.query.all()
        # survey_schema = SurveySchema(many=True)
        # output = survey_schema.dump(surveys)
        surveys = [survey.serialize for survey in Survey.query.all()]
        return jsonify(surveys)


def validate_request(request):
    """
    validate request data sent to '/survey' via 'post' before adding new survey to DB.
    """

    errors = []

    if not request.is_json:
        errors.append('You have to send a valid JSON')
        return errors
    else:
        survey_data = request.json

    name = survey_data.get('name')
    if not name:
        errors.append('You must provide a survey name')
    
    start_date = survey_data.get('start_date')
    if not start_date:
        errors.append('You must provide a start_date')
    else:
        try:
            datetime.strptime(start_date, '%d/%m/%Y %H:%M')
        except ValueError:
            errors.append('Incorrect start_date format, should be (dd/mm/yyyy HH:MM)')
    
    end_date = survey_data.get('end_date')
    if end_date:
        try:
            datetime.strptime(end_date, '%d/%m/%Y %H:%M')
        except ValueError:
            errors.append('Incorrect end_date format, should be (dd/mm/yyyy HH:MM)')

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
