# garden-trading
GardenTrading allows gardeners to trade their produce with other gardeners who are growing different produce nearby. It encourages people to grow and source food locally. Gardeners can list their own produce and message other gardeners whose produce interests them. They can upload images of themselves and their produce, and find gardens close by to them using GMaps. They can manage listings and upload photos from the User Profile area of the application. They can also search for produce they are specifically interested by doing a full text search from the site's navigation bar.

GardenTrading features user to user messaging and produce listings generated with Jinja templating. It has sign up forms and a member login with password hashing to protect user information. It offers image uploading for user and produce profiles. GardenTrading also has full text search of produce listings using LunrJS.

Users find gardens offering produce near them from the Garden Areas page, which maps garden locations with markers and infowindows  generated from the data model using the GMaps API. The styling of the infowindow content was generated with a combo of Javascript and CSS.

The data model of users, produce, and messages uses PostgreSQL and SQLAlchemy. 

The user to user messaging  that is embedded in the produce listings pages uses Javascript localStorage on the client side to autofill the recipient's user info on the Send Message page. 

A user can manage their photos and produce listings from their profile page, with full create, read, and destroy functioning for their produce listings. They can also check any messages they received and reply from this area of the site.  

PyTest has been used on the back end for testing of the application.

The produce listings themselves were created using Bootstrap 4 cards. The image slider on the homepage uses JQuery to time the image sliding. 
