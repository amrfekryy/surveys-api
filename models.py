from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import ( BadSignature, SignatureExpired,
    TimedJSONWebSignatureSerializer as Serializer)
import random, string

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from db_credentials import DB_URI


# intialize app, connect DB 
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# random 32 char key to sign user tokens
token_secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))


class Survey(db.Model):
    __tablename__ = 'surveys'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)
    description = db.Column(db.String(), nullable=True)

    # relationship (User-Surveys)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", backref="surveys", lazy=True)

    def __repr__(self):
        return f'<Survey {self.id} : {self.name}>'

    def set_datetime(self, start_or_end, datetime_str):
        """turn datetime string into datetime object"""
        datetime_obj = datetime.strptime(datetime_str, '%d/%m/%Y %H:%M')
        if start_or_end == 'start':
            self.start_date = datetime_obj
        elif start_or_end == 'end':
            self.end_date = datetime_obj

    def get_datetime(self, start_or_end):
        """turn datetime object into datetime string"""
        if start_or_end == 'start':
            return self.start_date.strftime('%d/%m/%Y %H:%M')
        elif start_or_end == 'end':
            return self.end_date.strftime('%d/%m/%Y %H:%M')

    @property
    def serialize(self):
        """returns object data in easily serializable format"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'start_date': self.get_datetime('start'),
            'end_date': self.get_datetime('end'),
            'questions': [{'question': question.serialize} for question in self.questions]
        }


class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(), nullable=False)
    note = db.Column(db.String(), nullable=True)

    # relationship (Survey-Questions)
    survey_id = db.Column(db.Integer, db.ForeignKey("surveys.id"), nullable=False)
    survey = db.relationship("Survey", backref="questions", lazy=True)

    def __repr__(self):
        return f'<Question {self.id} : {self.body}>'

    @property
    def serialize(self):
        """returns object data in easily serializable format"""
        return {
            'body': self.body,
            'note': self.note
        }


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(), nullable = False)
    password_hash = db.Column(db.String())

    def hash_password(self, password):
        """hash password for a user and store it in db"""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """verify password against stored hash"""
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expiration=60 * 15):
        """
        generate an encrypted token that has the user id
        and a default expiration time of 15 minutes
        """
        s = Serializer(token_secret_key, expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod # will to be used before initializing a User object
    def verify_auth_token(token):
        """decrypt a token and returns the user id"""
        s = Serializer(token_secret_key)
        # catch invalid or expired token
        try:
            token_data = s.loads(token)
        except (BadSignature, SignatureExpired): 
            return None
        return token_data.get('id')
