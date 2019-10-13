# Surveys and Questions API

This is an API that enable users to GET data about surveys from a database or POST new surveys.

### Running the app:
1. Clone the repository locally.
2. Download dependencies: `pip install -r requirements.txt`.
3. Create a local relational database using the DB interactive shell (I use PostgreSQL).
4. Modify credentials and/or database URI in `db_credentials.py`.
5. Setup the database: `python db_setup.py`.
6. Run the application: `python app.py`

### Usage:
Anyone can `GET` data from `/survey` but only registered users can `POST` new surveys.   

- **_registration_**:   
`POST` a JSON containing `username` and `password` to `/register`.   
example: ```curl -X POST 'http://127.0.0.1:5000/register' -H 'content-type:application/json' -d '{"username":"Amr", "password":"123"}'```   
   
- **_getting a token_**:   
use your credentials to `GET` an authorization token from `/token`.   
example: `curl -u "Amr":"123" 'http://127.0.0.1:5000/token'`.   
tokens expire in 15 minutes. get a new token when yours expire.      

- **_creating new surveys_**:   
use your token to `POST` a new survey to `/survey`.      
example: `curl -u "<token>":"blank" 'http://127.0.0.1:5000/survey' -H 'content-type:application/json' -d '{"name":"My Survey", "start_date":"13/10/2019 04:00", "questions":[{"question":{"body":"Do you like my API?"}}]}'`   

Note: errors in you requests are handeled and you will get JSON feedback with the `errors` if any or `success` in case of no errors.
