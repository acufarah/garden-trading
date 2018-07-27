import unittest

from server import app
from model import db, example_data, connect_to_db


class GardenTests(unittest.TestCase):
    """Tests for my party site."""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

        # Connect to test database (uncomment when testing database)
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data (uncomment when testing database)
        db.create_all()
        example_data()


    def test_home(self):
        """Does homepage render?"""
        result = self.client.get("/")
        self.assertIn(b"Share and Trade From Your Garden", result.data)

    def test_no_login_yet(self):
        """Do login and sign up show on navbar"""
        result = self.client.get('/')
        self.assertIn(b'Sign Up', result.data)
        self.assertIn(b'Login', result.data)
        self.assertNotIn(b'Logout', result.data)

    def test_login_form(self):
        """Does the login page render?"""
        result= self.client.get("/login")
        self.assertIn(b"Login form", result.data)

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
        self.assertIn(b'Fruit Listings Directory', result.data)

    def test_garden_areas(self):
        """Does the garden area directory work?"""
        result = self.client.get('/garden_areas')
        self.assertIn(b'Find Gardens in', result.data)

    def test_herbs(self):
        """Does the herb listings directory work?"""
        result = self.client.get('/herbs')
        self.assertIn(b'Herb Listings', result.data)

    def test_img_upload(self):
        """Does the image upload page render?"""
        result = self.client.get('/users_profile/img_upload.html')
        self.assertIn(b'Upload', result.data)

    def test_messages(self):
        """Does the messages page render?"""
        # result= self.client.get('/users_profile/messages.html')
        # self.assertIn(b'Previous Messages', result.data)
        pass

    def test_new_listing(self):
        result = self.client.get('/new_listing/1')

    def test_nuts(self):
        """Does the nut listing directory render?"""
        result = self.client.get('/nuts')
        self.assertIn(b'Nut Listings', result.data)

    def test_produce_add(self):
        """Does the add produce page render?"""
        result = self.client.get('/users_profile/produce_add.html')
        self.assertIn(b'Date Available', result.data)

    def test_seeds(self):
        """Does the seeds directory render?"""
        result = self.client.get('/seeds')
        self.assertIn(b'Seed Listings', result.data)

    def test_sign_up(self):
        result = self.client.get('sign_up')
        self.assertIn(b'Sign Up Form', result.data)

    def test_users_profile(self):
        result = self.client.get('/users_profile/1')
        self.assertIn(b'User Profile', result.data)

    def test_vegetables(self):
        result = self.client.get('/vegetables')
        self.assertIn(b'Vegetable Listings', result.data)

class GardenTestsDatabase(unittest.TestCase):
    """Flask tests that use the database."""

    def setUp(self):
        """Stuff to do before every test."""

        self.client = app.test_client()
        app.config['TESTING'] = True

        # Connect to test database (uncomment when testing database)
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data (uncomment when testing database)
        db.create_all()
        example_data()

        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = 1

    def tearDown(self):
        """Do at end of every test."""

        # (uncomment when testing database)
        db.session.close()
        db.drop_all()

    # def test_games(self):
    #     # FIXME: test that the games page displays the game from example_data()
    #     result = self.client.get('/games')
    #     self.assertIn(b'Fibbage', result.data)


# class FlaskTestsLoggedIn(unittest.TestCase):
#     """Flask tests with user logged in to session."""
#     def setUp(self):
#         app.config['TESTING'] = True
#         app.config['SECRET_KEY'] = 'key'
#         self.client = app.test_client()

#         with self.client as c:
#             with c.session_transaction() as sess:
#                 sess['RSVP'] = True


if __name__ == "__main__":

    unittest.main()