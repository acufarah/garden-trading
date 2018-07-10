"""Model and database functions for Garden Trading App."""

from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime

db = SQLAlchemy()

##############################################################################
# Model definitions

class User(db.Model):
    """User of garden trading website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(64), nullable=False)
    fname = db.Column(db.String(55), nullable=False)
    lname = db.Column(db.String(55), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    zipcode = db.Column(db.String(15), nullable=False)
    #profile_pic = pass
    about_me = db.Column(db.Text, nullable=False)
    about_garden = db.Column(db.Text, nullable=False)

def __repr__(self):
    """Provide helpful representation when printed."""
    return f"<User user_id={self.user_id} email={self.email} >"

class Produce(db.Model):
	"""Produce available from gardens."""

	__tablename__ = "produce"

	prod_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
	#prod_pic = pass
	prod_name = db.Column(db.String(120), nullable=False)
	prod_type = db.Column(db.Integer, nullable=True)
	describe = db.Column(db.Text, nullable=False)
	avail_date = db.Column(db.Date, nullable=False)

	user = db.relationship("User", backref=db.backref("produce", order_by=prod_id))

def __repr__(self):
    """Provide helpful representation when printed."""
    return f"<Produce prod_id={self.prod_id} user_id={self.user_id} prod_name={self.prod_name} >"

"""class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Message {}>'.format(self.body)"""





def init_app():
    # So that we can use Flask-SQLAlchemy, we'll make a Flask app.
    from flask import Flask
    app = Flask(__name__)

    connect_to_db(app)
    print("Connected to DB.")


def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our database.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///garden'
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print("Connected to DB.")