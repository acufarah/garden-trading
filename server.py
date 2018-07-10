"""Garden trading app."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension

from model import User, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

app.jinja_env.undefined = StrictUndefined

@app.route('/')
def index():
    """Homepage."""
    
    return render_template("home.html")

@app.route('/sign_up', methods=["GET"])
def sign_up():
	"""Sign up page."""

	return render_template("sign_up.html")

@app.route('/sign_up', methods=["POST"])
def sign_up_process():
	"""Sign up process."""

	fname = request.form.get('fname')
	lname = request.form.get('lname')
	address = request.form.get('address')
	city = request.form.get('city')
	state = request.form.get('state')
	zipcode = request.form.get('zipcode')
	username = request.form.get('username')
	email = request.form.get('email')
	password = request.form.get('password')

	if User.query.filter_by(username='username').first():
		flash("User with this username already exists.")
	elif User.query.filter_by(email='email').first():
		flash("User with this email already exists.")
		return redirect('/')
	else:
		new_user = User(username=username, email=email, password=password, fname=fname, lname=lname,
						address=address, city=city, state=state, zipcode=zipcode)
		db.session.add(new_user)
		db.session.commit()
		flash("User added to database. Please log in.")
		return redirect('/login')

@app.route('/login', methods=["POST"])
def process_login_form():
	email = request.form.get('email')
	password = request.form.get('password')


	user = User.query.filter_by(email=email, password=password).first()
	if user:
		flash("Login successful.")
		session['user_id'] = user.user_id
		return redirect('/users_profile/{}'.format(user.user_id))
	else:
		flash("Login unsuccessful.")
		return redirect('/login')

@app.route('/login')
def show_login_form():
	return render_template("login.html")


@app.route('/users/<int:uid>')
def show_user_info(uid):

	print("User UID is: {}".format(uid))

	user = User.query.get(uid)

	return render_template('user_profile.html', user=user, username=user.username, email=user.email, password=user.password, fname=user.fname, lname=user.lname,
						address=user.address, city=user.city, state=user.state, zipcode=user.zipcode)



















if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')