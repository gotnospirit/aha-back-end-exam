import json
from os import path
from flask import flash
from flask_login import current_user, login_user
from flask_dance.contrib.google import make_google_blueprint
from flask_dance.contrib.facebook import make_facebook_blueprint
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from .models import db, OAuth, User
import os


google_config = {}
try:
    google_filepath = path.join(path.dirname(__file__), "../google.json")
    with open(google_filepath) as f:
        web_config = json.load(f)['web']
        if 'client_id' in web_config and 'client_secret' in web_config:
            google_config = {
                'client_id': web_config['client_id'],
                'client_secret': web_config['client_secret']
            }
except:
    flash("Failed to read 'google.json'")

google_blueprint = make_google_blueprint(
    **google_config,
    reprompt_consent=True,
    scope=["profile", "email"],
    storage=SQLAlchemyStorage(OAuth, db.session, user=current_user)
)


facebook_config = {}
fb_cid = os.getenv('FACEBOOK_OAUTH_CLIENT_ID', None)
fb_cs = os.getenv('FACEBOOK_OAUTH_CLIENT_SECRET', None)
if fb_cid and fb_cs:
    facebook_config = {
        'client_id': fb_cid,
        'client_secret': fb_cs
    }

facebook_blueprint = make_facebook_blueprint(
    **facebook_config,
    scope=["public_profile", "email"],
    storage=SQLAlchemyStorage(OAuth, db.session, user=current_user)
)


endpoints = {
    google_blueprint.name: "/oauth2/v1/userinfo",
    facebook_blueprint.name: "/me?fields=id,name,email"
}


# create/login local user on successful OAuth login
@oauth_authorized.connect_via(google_blueprint)
@oauth_authorized.connect_via(facebook_blueprint)
def oauth_authorized_fn(blueprint, token):
    if not token:
        flash("Failed to log in.")
        return False

    resp = blueprint.session.get(endpoints[blueprint.name])
    if not resp.ok:
        flash("Failed to fetch user info.")
        return False

    oauth_info = resp.json()

    # for key, value in oauth_info.items():
    #     print(key, value)

    # For Google OAuth, oauth_info contains:
    #     id                -> Google user_id (int)
    #     email             -> User's email address (str)
    #     verified_email    -> Account is verified (bool)
    #     name              -> User's fullname (str)
    #     given_name        -> User's firstname (str)
    #     family_name       -> User's lastname (str)
    #     picture           -> User's profile thumbnail (str)
    #     locale            -> User's preferred language (str)

    # For Facebook Login, oauth_info contains:
    #     id                -> Facebook user_id (int)
    #     name              -> User's fullname (str)
    #     email             -> User's email address (str)

    if 'email' not in oauth_info:
        flash("This application requires your email address.")
        return False

    provider_user_id = oauth_info['id']
    user = OAuth.FindUser(blueprint.name, provider_user_id)
    if user:
        user.on_logged_in()
        login_user(user, remember=True)
    else:
        email = oauth_info['email']
        nickname = oauth_info.get('name', email[:email.find("@")])
        oauth = OAuth.Create(blueprint.name, provider_user_id, token)
        user = User.CreateWithOAuth(email, nickname, oauth)
        login_user(user, remember=True)

    # Disable Flask-Dance's default behavior for saving the OAuth token
    return False


# notify on OAuth provider error
@oauth_error.connect_via(google_blueprint)
@oauth_error.connect_via(facebook_blueprint)
def oauth_error_fn(blueprint, message, response):
    msg = ("OAuth error from {name}! " "message={message} response={response}").format(
        name=blueprint.name, message=message, response=response
    )
    flash(msg)
