from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db
from db_credentials import DB_URI

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


def main():
    db.drop_all()
    db.create_all()
    print("\nDatabase setup completed successfully\n")


if __name__ == "__main__":
    with app.app_context():
        main()
