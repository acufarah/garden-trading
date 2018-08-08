import unittest

from server import app
from model import db, example_data, connect_to_db, Bcrypt
from geopy.geocoders import Nominatim

class GardenTests(unittest.TestCase):
    """Tests for my party site."""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

        # Connect to test database (uncomment when testing database)
        connect_to_db(app, "postgresql:///testdb")
        bcrypt = Bcrypt(app)
        # Create tables and add sample data (uncomment when testing database)
        db.drop_all()
        db.create_all()
        example_data(bcrypt)


    def test_home(self):
        """Does homepage render?"""
        result = self.client.get("/")
        self.assertIn(b'<img class="image-fluid" src="static/images/home-heading.jpg">', result.data)

    def test_no_login_yet(self):
        """Do login and sign up show on navbar"""
        result = self.client.get('/')
        self.assertIn(b'Sign Up', result.data)
        self.assertIn(b'Login', result.data)
        self.assertNotIn(b'Logout', result.data)

    def test_login_form(self):
        """Does the login page render?"""
        result= self.client.get("/login")
        self.assertIn(b"Login Form", result.data)

    def test_login(self):
        """Does the login work?"""
        result = self.client.post("/login",
                                data={'email': "gardenlover@gmail.com",
                                'password': "gardenlover"},
                                follow_redirects=True)
        self.assertIn(b'Login successful', result.data)

    def test_fruits(self):
        """Does the fruit directory work?"""
        result = self.client.get('/fruits')
        self.assertIn(b'<img class="image-fluid" src="static/images/fruit-heading.jpg">', result.data)

    def test_garden_areas(self):
        """Does the garden area directory work?"""
        result = self.client.get('/garden_areas')
        self.assertIn(b'Find Gardens in', result.data)

    def test_herbs(self):
        """Does the herb listings directory work?"""
        result = self.client.get('/herbs')
        self.assertIn(b'<img class="image-fluid" src="static/images/herb-heading.jpg">', result.data)

    def test_img_upload(self):
        """Does the image upload page render?"""
        result = self.client.get('/users_profile/img_upload.html')
        self.assertIn(b'Upload', result.data)

    def test_messages(self):
        """Does the messages page render?"""
        # result= self.client.get('/users_profile/messages.html')
        # self.assertIn(b'Previous Messages', result.data)
        pass

    def test_my_listings(self):
        result = self.client.get('/users_profile/my_listings.html')
        self.assertIn(b'<img class="image-fluid" src="../static/images/my-prod-heading.jpg">', result.data)

    def test_new_listing(self):
        result = self.client.get('/new_listing/1')
        self.assertIn(b'<a href="users_profile/img_upload.html">Add a photo of your produce or garden</a>', result.data)

    def test_nuts(self):
        """Does the nut listing directory render?"""
        result = self.client.get('/nuts')
        self.assertIn(b'<img class="image-fluid" src="static/images/nut-heading.jpg">', result.data)

    def test_produce_add(self):
        """Does the add produce page render?"""
        result = self.client.get('/users_profile/produce_add.html')
        self.assertIn(b'Date Available', result.data)

    def test_seeds(self):
        """Does the seeds directory render?"""
        result = self.client.get('/seeds')
        self.assertIn(b'<img class="image-fluid" src="static/images/seed-heading.jpg">', result.data)

    def test_sign_up(self):
        result = self.client.get('sign_up')
        self.assertIn(b'Sign Up Form', result.data)

    def test_users_profile(self):
        result = self.client.get('/users_profile/1')
        self.assertIn(b'Add a Profile Picture', result.data)

    def test_vegetables(self):
        result = self.client.get('/vegetables')
        self.assertIn(b'<img class="image-fluid" src="static/images/vegetable-heading.jpg">', result.data)

class GardenTestsDatabase(unittest.TestCase):
    """Flask tests that use the database."""

    def setUp(self):
        """Stuff to do before every test."""

        self.client = app.test_client()
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'key'
        # Connect to test database (uncomment when testing database)
        connect_to_db(app, "postgresql:///testdb")
        bcrypt = Bcrypt(app)
        # Create tables and add sample data (uncomment when testing database)
        db.drop_all()
        db.create_all()
        example_data(bcrypt)

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 1

    def test_sign_up_process(self):
        """Does the database add a new user?"""
        # password = bcrypt.generate_password_hash("flowerpower")
        full_address = '122 Holly Court, Mountain View, CA, 94043'
        geolocator = Nominatim()
        location = geolocator.geocode(full_address)
        latitude = location.latitude
        longitude = location.longitude
        result = self.client.post('/sign_up',
                                  data={'fname': 'Flower', 'lname': 'Powers',
                                  'email':'flowerpower@gmail.com',
                                  'username': 'flowerpower',
                                  'address':'122 Holly Court',
                                  'city': 'Mountain View',
                                  'state':'CA',
                                  'zipcode':'94043',
                                  'full_address': full_address,
                                  'password': 'flowerpower',
                                  'latitude': latitude,
                                  'longitude': longitude},
                                   follow_redirects=True)
        self.assertIn(b"User added to database. Please log in.", result.data)

    def test_users_profile(self):
        """Does the user profile page render using the user id in session"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 1
              

        result = self.client.get('/users_profile/{}'.format(sess['user_id']))
        self.assertIn(b'Add a Profile Picture', result.data)

    def test_login_process(self):
        pass

    def test_after_login(self):
        """Do login and sign up show on navbar"""
        result = self.client.get('/')
        self.assertNotIn(b'Sign Up', result.data)
        self.assertNotIn(b'Login', result.data)
        self.assertIn(b'Logout', result.data)

    def test_logout(self):
        """Test logout process"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 1

        if 'user_id' in sess:
            sess.pop('user_id', None)

            result = self.client.get('/logout', follow_redirects=True)
            self.assertIn(b'You are now logged out', result.data)
        
        else:
            result = self.client.get('/login')
            self.assertIn(b'You are not logged in', result.data)

    def test_img_upload_process(self):
        """Does image uploading work?"""
        pass

    def test_prod_add_process(self):
        """Does adding a produce listing work?"""
        pass

    def test_send_message_process(self):
        """Does sending messages work?"""
        pass

    def tearDown(self):
        """Do at end of every test."""
        db.session.close()
        db.drop_all()


if __name__ == "__main__":

    unittest.main()