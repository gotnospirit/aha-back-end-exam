import os
from flask import Flask
from flask_login import LoginManager
from www.models import db, User
from www.mailer import Mailer

app = Flask(__name__)

app.config['SERVER_NAME'] = os.getenv('SERVER_NAME', 'localhost:5000')
app.config['PREFERRED_URL_SCHEME'] = os.getenv('PREFERRED_URL_SCHEME', 'http')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your secret key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

mailer = Mailer('smtp.gmail.com', 465, os.getenv('GMAIL_PASSWORD',
                '123456789'), os.getenv('GMAIL_ADDRESS', 'my@example.com'), app.logger)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


from www import routes
