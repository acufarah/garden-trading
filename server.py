"""Garden trading app."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, jsonify, url_for, flash, session)
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug import secure_filename
from model import User, Produce, connect_to_db, db

app = Flask(__name__)
app.config.from_object(__name__)
app.config['UPLOAD_FOLDER'] = 'upload'

ALLOWED_EXTENSIONS = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif']
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


@app.route('/users_profile/<int:uid>')
def show_user_info(uid):

	print("User UID is: {}".format(uid))

	user = User.query.get(uid)

	return render_template('users_profile.html', user=user, username=user.username, email=user.email, password=user.password, fname=user.fname, lname=user.lname,
						address=user.address, city=user.city, state=user.state, zipcode=user.zipcode)

@app.route('/logout')
def logout():
	if 'user_id' in session:
		session.pop('user_id', None)
		flash('You are now logged out')
		return redirect('/')
	else:
		flash('You are not logged in')
		return redirect('/login')

@app.route('/users_profile/produce_add.html', methods=["GET"])
def produce_add():
	"""Sign up page."""

	return render_template("produce_add.html")

@app.route('/produce_add', methods=["POST"])
def produce_add_process():
	"""Sign up process."""

	prod_name = request.form.get('prod_name')
	prod_type = request.form.get('prod_type')
	avail_date = request.form.get('avail_date')
	describe = request.form.get('describe')

	new_produce = Produce(prod_name=prod_name, prod_type=prod_type, avail_date=avail_date, describe=describe)
	db.session.add(new_produce)
	db.session.commit()
	flash("Produce successfully added to database")
	return redirect('/new_listing')

@app.route('/new_listing')
def new_listing():
	"""Shows newly made produce listing."""
	produce = db.session.query(Produce).order_by(Produce.prod_id.desc()).first()
	return render_template('/new_listing.html', prod_name=produce.prod_name, prod_type=produce.prod_type, avail_date=produce.avail_date, describe=produce.describe)

@app.route('/vegetables')
def veg_directory():
	"""Directory of vegetable listings"""
	vegetables = Produce.query.filter_by(prod_id=1).all()
	return render_template('/vegetables.html', vegetables=vegetables)

@app.route('/fruits')
def fruit_directory():
	"""Directory of fruit listings"""
	fruits = Produce.query.filter_by(prod_id=2).all()
	return render_template('/fruits.html', fruits=fruits)

@app.route('/nuts')
def nut_directory():
	"""Directory of nut listings"""
	nuts = Produce.query.filter_by(prod_id=5).all()
	return render_template('/nuts.html', nuts=nuts)

@app.route('/seeds')
def seed_directory():
	"""Directory of seed listings"""
	seeds = Produce.query.filter_by(prod_id=4).all()
	return render_template('/seeds.html')

@app.route('/herbs')
def herbs_directory():
	"""Directory of herb listings"""
	herbs = Produce.query.filter_by(prod_id=3).all()
	return render_template('/herbs.html')

@app.route('/garden_areas')
def garden_directory():
	"""Directory of garden listings"""
	return render_template('/garden_areas.html')

@app.route('/users_profile/img_upload.html')
def img_upload():
	"""Directory of garden listings"""
	return render_template('/img_upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            now = datetime.now()
            filename = os.path.join(app.config['UPLOAD_FOLDER'], "%s.%s" % (now.strftime("%Y-%m-%d-%H-%M-%S-%f"), file.filename.rsplit('.', 1)[1]))
            file.save(filename)
            return jsonify({"success":True})

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS











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