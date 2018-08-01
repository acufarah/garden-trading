"""Model and database functions for Garden Trading App."""
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime
# from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

db = SQLAlchemy()
##############################################################################
# Model definitions

class User(db.Model):
    """User of garden trading website."""
    __tablename__ = "users"
    __searchable__ = ['username', 'zipcode', 'about_me', 'about_garden']

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    password = db.Column(db.Binary(128), nullable=False)
    fname = db.Column(db.String(55), nullable=False)
    lname = db.Column(db.String(55), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    zipcode = db.Column(db.String(15), nullable=False)
    full_address = db.Column(db.String(320), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    usr_img= db.Column(db.String, default=None, nullable=True)
    usr_img_url = db.Column(db.String, default=None, nullable=True)
    about_me = db.Column(db.Text, nullable=True)
    about_garden = db.Column(db.Text, nullable=True)
    gard_img= db.Column(db.String, default=None, nullable=True)
    gard_img_url = db.Column(db.String, default=None, nullable=True)


    #Create relationships for messaging.

    messages_sent = db.relationship('Message',
                                    foreign_keys='Message.sender_id',
                                    backref='sender', lazy='dynamic')
    messages_received = db.relationship('Message',
                                        foreign_keys='Message.recipient_id',
                                        backref='recipient', lazy='dynamic')
    last_message_read_time = db.Column(db.DateTime)

    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient=self).filter(
            Message.timestamp > last_read_time).count()

    """def set_password(self, password):
    	self.password_hash = generate_password_hash(password)

    #def check_password(self, password):
    	return check_password_hash(self.password_hash, password)"""

def __repr__(self):
    """Provide helpful representation when printed."""
    return f"<User user_id={self.user_id} email={self.email} >"

class Produce(db.Model):
    """Produce available from gardens."""
    __tablename__ = "produce"
    __searchable__ = ['prod_name', 'prod_type', 'describe', 'avail_date']

    prod_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    prod_img= db.Column(db.String, default=None, nullable=True)
    prod_img_url = db.Column(db.String, default=None, nullable=True)
    prod_name = db.Column(db.String(120), nullable=False)
    prod_type = db.Column(db.Integer, nullable=True)
    describe = db.Column(db.Text, nullable=False)
    avail_date = db.Column(db.Date, nullable=False)

    user = db.relationship("User", backref=db.backref("produce", order_by=prod_id))

def __repr__(self):
    """Provide helpful representation when printed."""
    return f"<Produce prod_id={self.prod_id} user_id={self.user_id} prod_name={self.prod_name} >"

class Message(db.Model):
    """For user messaging system."""
    __tablename__= "messages"

    message_id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    sender_username = db.Column(db.String(120), nullable = False)
    recipient_username = db.Column(db.String(120), nullable = False)
    body = db.Column(db.String(200), nullable = False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

def __repr__(self):
        return '<Message {}>'.format(self.body)


def connect_to_db(app, db_uri= 'postgres:///garden'):
    """Connect the database to our Flask app."""
    # Configure to use our database.
    
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    db.app = app
    db.init_app(app)
    migrate = Migrate(app, db)


def example_data(bcrypt):
    """Create example data for the test database."""
    password = bcrypt.generate_password_hash("gardenlover")
    user1 = User(username="gardenlover", email="gardenlover@gmail.com",
                 fname="Jane", lname="Garden", address="3120 De La Cruz Blvd", 
                 city="Santa Clara", state="CA", zipcode=95054, 
                 password=password) 
    db.session.add(user1)
    password2 = bcrypt.generate_password_hash("herbie")
    user2= User(username="herbie", email="herbie@gmail.com", 
                
                fname="Herb", lname="Garden", address="3120 De la Cruz Blvd", city="Santa Clara", state="CA", zipcode=95054, 
                password=password2)
    db.session.add(user2)
    produce1= Produce(user_id=1, prod_name='tomatoes', prod_type= 1, describe='Yummy organic brandywine tomatoes', avail_date='08/01/2018')
    db.session.add(produce1)
    db.session.commit()


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.
    from flask import Flask

    app = Flask(__name__)

    connect_to_db(app)
    print("Connected to DB.")