"""Garden trading app."""
import requests
from datetime import datetime
import geopy.geocoders
from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, json, jsonify, url_for, flash, session)
import os
import geojson
from lunr import lunr
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug import secure_filename
from geopy.geocoders import Nominatim
from model import User, Produce, Message, connect_to_db, db, Bcrypt

#from model import UserSchema, ProduceSchema, MessageSchema


app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config.from_object(__name__)
app.config['UPLOAD_FOLDER'] = "/gardenproject/static/uploads"

ALLOWED_EXTENSIONS = set([ 'png', 'jpg', 'jpeg'])
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
    full_address = ('{}, {}, {}, {}'.format(address, city, state, zipcode))
    geolocator = Nominatim()
    location = geolocator.geocode(full_address)
    latitude = location.latitude
    longitude = location.longitude
    pw_hash = bcrypt.generate_password_hash(password)
    about_me = request.form.get('about_me')
    about_garden = request.form.get('about_garden')

    if User.query.filter_by(username='username').first():
        flash("User with this username already exists.")
    elif User.query.filter_by(email='email').first():
        flash("User with this email already exists.")
        return redirect('/')
    else:
        #Store new user info in DB
        new_user = User(username=username, email=email, password=pw_hash, fname=fname, lname=lname,
                        address=address, city=city, state=state, zipcode=zipcode, full_address=full_address, latitude=latitude, longitude=longitude,
                        about_me=about_me, about_garden=about_garden)
        db.session.add(new_user)
        db.session.commit()
        flash("User added to database. Please log in.")
        return redirect('/login')

@app.route('/login', methods=["POST"])
def process_login_form():
    """Get information from login form"""
    email = request.form.get('email')
    password1 = request.form.get('password')


    user = User.query.filter_by(email=email).first()
    if user:
        authenticated_user = bcrypt.check_password_hash(user.password, password1)
        if authenticated_user:
            flash("Login successful.")
            session['user_id'] = user.user_id
            return redirect('/users_profile/{}'.format(user.user_id))
    else:
        flash("Login unsuccessful.")
        return redirect('/login')

@app.route('/login')
def show_login_form():
    """Render login form"""
    return render_template("login.html")


@app.route('/users_profile/<int:uid>')
def show_user_info(uid):
    """render user profile"""
    print("User UID is: {}".format(uid))

    user = User.query.get(uid)

    return render_template('users_profile.html', user=user, username=user.username, email=user.email, password=user.password, fname=user.fname, lname=user.lname,
                        address=user.address, city=user.city, state=user.state, zipcode=user.zipcode, usr_img=user.usr_img)

@app.route('/logout')
def logout():
    """Create logout process"""
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

@app.route('/produce_add.html', methods=["POST"])
def produce_add_process():
    """Sign up process."""

    prod_name = request.form.get('prod_name')
    prod_type = request.form.get('prod_type')
    avail_date = request.form.get('avail_date')
    describe = request.form.get('describe')
    user_id = session.get('user_id')

    new_produce = Produce(prod_name=prod_name, prod_type=prod_type, avail_date=avail_date, describe=describe, user_id=user_id)
    db.session.add(new_produce)
    db.session.commit()
    flash("Produce successfully added to database")
    return redirect('/new_listing')

@app.route('/new_listing')
def new_listing():
    """Shows newly made produce listing."""
    produce = db.session.query(Produce).order_by(Produce.prod_id.desc()).first()
    current_user = User.query.filter(User.user_id== session['user_id']).first()
    return render_template('/new_listing.html', prod_name=produce.prod_name, prod_type=produce.prod_type, 
                            avail_date=produce.avail_date, describe=produce.describe, gardener=current_user.username, prod_img=produce.prod_img)

@app.route('/vegetables')
def veg_directory():
    """Directory of vegetable listings"""
    vegetables = Produce.query.filter_by(prod_type=1).all()
    return render_template('/vegetables.html', vegetables=vegetables)

@app.route('/fruits')
def fruit_directory():
    """Directory of fruit listings"""
    fruits = Produce.query.filter_by(prod_type=2).all()
    return render_template('/fruits.html', fruits=fruits)

@app.route('/nuts')
def nut_directory():
    """Directory of nut listings"""
    nuts = Produce.query.filter_by(prod_type=5).all()
    return render_template('/nuts.html', nuts=nuts)

@app.route('/seeds')
def seed_directory():
    """Directory of seed listings"""
    seeds = Produce.query.filter_by(prod_type=4).all()
    return render_template('/seeds.html', seeds=seeds)

@app.route('/herbs')
def herbs_directory():
    """Directory of herb listings"""
    herbs = Produce.query.filter_by(prod_type=3).all()
    return render_template('/herbs.html', herbs=herbs)

@app.route('/garden_areas')
def garden_directory():
    """Directory of garden listings"""
    gardeners = db.session.query(User).order_by(User.user_id.desc()).first()
    return render_template('/garden_areas.html', gardeners=gardeners)

@app.route('/garden_areas.json')
def address_map():
    """Transform address data from DB to plot on GMaps."""
    users = User.query.all()
    feature_lst = []
    for user in users:
        lat = user.latitude
        lng = user.longitude
        username = user.username
        zipcode = user.zipcode
        gard_info = user.about_me
        loc_point = geojson.Point((user.longitude, user.latitude))
        loc_properties = dict(name=username, zipcode=zipcode, info=gard_info)
        loc_json = geojson.Feature(geometry=loc_point, properties=loc_properties)
        feature_lst.append(loc_json)
    locs_json = geojson.FeatureCollection(feature_lst)
    return jsonify(locs_json)

@app.route('/base.json')
def full_text_search():
    """Make an index of information that can be used by lunr.js on the client side for full-text search"""
    documents = []
    produce = Produce.query.all()
    for p in produce:
        name = p.prod_name
        p_type = p.prod_type
        p_describe = p.describe
        p_date = p.avail_date
        p.id = str(p.prod_id)
        body = dict(type=p_type, name=name, date=p_date)
        lunr_ready = dict( id=p.id, title=name, body=body)
        documents.append(lunr_ready)
    #idx = lunr( ref='id', fields=('title', 'body'), documents=documents)
    return jsonify(documents)

@app.route('/search_results', methods=['GET','POST'])
def search_results():
    """Render search results from search input"""
    query = request.form.get('search')
    documents = []
    produce = Produce.query.all()
    for p in produce:
        name = p.prod_name
        p_type = p.prod_type
        p_describe = p.describe
        p_date = p.avail_date
        p.id = str(p.prod_id)
        body = dict(type=p_type, name=name, date=p_date, describe=p_describe)
        lunr_ready = dict( id=p.id, title=name, body=body)
        documents.append(lunr_ready)


    idx = lunr( ref='id', fields=('title', 'body'), documents=documents )
    results= idx.search(query)
    prod = []
    for result in results:
        ref = int(result.get('ref'))
        p = Produce.query.filter(Produce.prod_id == ref ).one()
        prod.append(p)
    if prod == []:
        flash("There are no results that match your search request")
        return redirect('/')
    else:
        return render_template('/search_results.html',
                           query=query,
                           results=results,
                           prod=prod)

@app.route('/users_profile/img_upload.html')
def img_upload_form():
    """Create the image upload page and form"""
    return render_template('/img_upload.html')

@app.route('/users_profile/img_upload.html', methods=['POST'])
def img_upload():
    """Image uploader for site"""
    if 'user_id' in session:
        user_id = session.get('user_id')

        f1 = request.files.get('usr_img')
        if f1!= None:
            filename1 = secure_filename(f1.filename)
            f1.save(os.path.join(app.config['UPLOAD_FOLDER'], "profile_pics/", filename1))
            user_in_session = User.query.get(user_id)
            user_in_session.usr_img = filename1
            user_in_session.user_img_url = f"{(app.config['UPLOAD_FOLDER'])}//profile_pics//{filename1}"
            db.session.commit()
            flash("Photo uploaded and stored successfully") 
            return redirect('/users_profile/{}'.format(user_id))
    
        f2 = request.files.get('prod_img')
        if f2!= None:
            filename2 = secure_filename(f2.filename)
            f2.save(os.path.join(app.config['UPLOAD_FOLDER'], "prod_img/", filename2))
            produce = db.session.query(Produce).order_by(Produce.prod_id.desc()).first()
            produce.prod_img = filename2
            produce.prod_img_url = f"{(app.config['UPLOAD_FOLDER'])}//prod_img//{filename2}"
            db.session.commit()
            flash("Photo uploaded and stored successfully")
            return redirect('/new_listing') 

        f3 = request.files.get('gard_img')
        if f3!= None:
            filename3 = secure_filename(f3.filename)
            f3.save(os.path.join(app.config['UPLOAD_FOLDER'], "gard_img/", filename3))
            user_in_session = User.query.get(user_id)
            user_in_session.gard_img = filename3
            user_in_session.gard_img_url = f"{(app.config['UPLOAD_FOLDER'])}//gard_img//{filename3}"
            db.session.commit()
            flash("Photo uploaded and stored successfully")
            return redirect('/users_profile/{}'.format(user_id))

        if f1 == None and f2 == None and f3 == None:
            flash("Something went wrong with your photo upload. Try again")
            return redirect('/users_profile/img_upload.html')



@app.route('/send_message')
def send_message_form():
    """Render message form"""
    return render_template('send_message.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    """Get message input to store and send"""
    username1 = request.form.get('recipient_username')
    username = username1.lower()
    user = User.query.filter_by(username=username).first_or_404()
    current_user = User.query.filter(User.user_id== session['user_id']).first()
    sender = current_user
    body = request.form.get('body')
    msg = Message(sender=sender, recipient=user, recipient_username=user.username,
                  body=body, sender_username=current_user.username)
    db.session.add(msg)
    db.session.commit()
    flash('Your message has been sent.')
    return redirect('/')

@app.route('/users_profile/messages.html')
def messages():
    """Check messages route"""
    if 'user_id' in session:
        u_id = session.get('user_id')
        current_user = User.query.filter(User.user_id == session['user_id'])
        current_user.last_message_read_time = datetime.utcnow()
        db.session.commit()
        #messages = current_user.messages_received.order_by(Message.timestamp.desc())
        messages = Message.query.filter(Message.recipient_id == u_id).order_by(Message.message_id.desc())
        message = messages.first()
        if message == None:
            flash('You have no messages')
            return redirect('/users_profile/{}'.format(u_id))
        else:
            return render_template('messages.html', messages=messages, current_user=current_user, message= message)  

@app.route('/users_profile/my_listings.html', methods=["GET"])
def my_listings():
    """My Listings Route"""
    if 'user_id' in session:
        u_id = session.get('user_id')
        current_user = User.query.filter(User.user_id == session['user_id'])
        user_produce_listings = Produce.query.filter(Produce.user_id == u_id).order_by(Produce.prod_id.desc())        
        if user_produce_listings == None:
            flash('You have no produce listings')
            return redirect('/users_profile/{}'.format(u_id))     
        else:    
            return render_template('my_listings.html', listings=user_produce_listings, current_user=current_user) 


@app.route('/users_profile/my_listings.html', methods=["POST"])
def delete_listing():
    """Delete a Produce Listing"""
    if 'user_id' in session:
        user_id = session.get('user_id')

        user_produce_listing_id = request.form.get("listing")
        produce = Produce.query.filter(Produce.prod_id == user_produce_listing_id).first()
        db.session.delete(produce)
        db.session.commit()
        flash('Your listing was successfully deleted.')
        return redirect('/users_profile/{}'.format(user_id))

    # @app.route('/users_profile/my_listings/update_listing.html', methods=["GET","POST"])
# def update_listing():
#     """Update a Produce Listing"""
#     if 'user_id' in session:
#         user_id = session.get('user_id')

#         user_produce_listing_id = request.form.get("listing")
#         produce = Produce.query.filter(Produce.prod_id == user_produce_listing_id).first()
#         description = produce.describe
#         updated_description = request.form.get("d_update")
#         date = produce.prod_date
#         updated_date = request.form.get("date_update")
#         if updated_description is not None:
#             description = updated_description
#             db.session.commit()
#             return jsonify({'Description': description})
#         if updated_date is not None:
#             date = updated_date
#             db.session.commit()
#             return jsonify({'Available' : date})


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = False
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)
   
    # Use the DebugToolbar
    DebugToolbarExtension(app)
    app.run(port=5000, host='0.0.0.0')