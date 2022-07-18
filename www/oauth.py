import json
from os import path
from flask import flash
from flask_login import current_user, login_user
from flask_dance.contrib.google import make_google_blueprint
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from .models import db, OAuth, User


google_filepath = path.join(path.dirname(__file__), "../google.json")
with open(google_filepath) as f:
    google_config = json.load(f)['web']


google_blueprint = make_google_blueprint(
    client_id=google_config['client_id'],
    client_secret=google_config['client_secret'],
    reprompt_consent=True,
    scope=["profile", "email"],
    storage=SQLAlchemyStorage(OAuth, db.session, user=current_user)
)


# create/login local user on successful OAuth login
@oauth_authorized.connect_via(google_blueprint)
def google_logged_in(blueprint, token):
    if not token:
        flash("Failed to log in.")
        return False

    resp = blueprint.session.get("/oauth2/v1/userinfo")
    if not resp.ok:
        flash("Failed to fetch user info.")
        return False

    oauth_info = resp.json()

    # for key, value in oauth_info.items():
    #     print(key, value)

    # For Google OAuth, oauth_info contains:
    #     id                -> OAuth provider's user_id (int)
    #     email             -> User's email address (str)
    #     verified_email    -> Account is verified (bool)
    #     name              -> User's fullname (str)
    #     given_name        -> User's firstname (str)
    #     family_name       -> User's lastname (str)
    #     picture           -> User's profile thumbnail (str)
    #     locale            -> User's preferred language (str)

    if 'email' not in oauth_info:
        flash("This application requires your email address.")
        return False

    user = OAuth.FindUser(blueprint.name, oauth_info["id"])
    if user:
        user.on_logged_in()
        login_user(user, remember=True)
    else:
        oauth = OAuth.Create(blueprint.name, oauth_info["id"], token)
        user = User.CreateWithOAuth(
            oauth_info['email'], oauth_info['name'], oauth)
        login_user(user, remember=True)

    # Disable Flask-Dance's default behavior for saving the OAuth token
    return False


# notify on OAuth provider error
@oauth_error.connect_via(google_blueprint)
def google_error(blueprint, message, response):
    msg = ("OAuth error from {name}! " "message={message} response={response}").format(
        name=blueprint.name, message=message, response=response
    )
    flash(msg)
