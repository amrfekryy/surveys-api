from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Survey(db.Model):
    __tablename__ = 'surveys'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)
    description = db.Column(db.String(), nullable=True)

    questions = db.relationship("Question", backref="survey", lazy=True)

    def __repr__(self):
        return f'<Survey {self.id} : {self.name}>'

    def set_datetime(self, start_or_end, datetime_str):
        datetime_object = datetime.strptime(datetime_str, '%d/%m/%Y %H:%M')
        if start_or_end == 'start':
            self.start_date = datetime_object
        elif start_or_end == 'end':
            self.end_date = datetime_object

    def get_datetime(self, start_or_end):
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

    survey_id = db.Column(db.Integer, db.ForeignKey("surveys.id"), nullable=False)

    def __repr__(self):
        return f'<Question {self.id} : {self.body}>'

    @property
    def serialize(self):
        """returns object data in easily serializable format"""
        return {
            'body': self.body,
            'note': self.note
        }
