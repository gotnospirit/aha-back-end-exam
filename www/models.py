from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import bcrypt


db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(
        db.DateTime, server_default=db.func.current_timestamp())
    signin_count = db.Column(db.Integer, default=0)
    last_signin_at = db.Column(
        db.DateTime, server_default=db.func.current_timestamp())
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    pwd_salt = db.Column(db.String(255), nullable=False)
    nickname = db.Column(db.String(255), nullable=False)
    activation_key = db.Column(db.String(255), nullable=True)
    activated_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"User('{self.nickname}', '{self.email }')"

    def is_activated(self) -> bool:
        return self.activated_at is not None

    def can_send_verification(self) -> bool:
        return not self.is_activated() and self.activation_key is not None

    def update_password(self, password: str) -> None:
        salt = bcrypt.gensalt()
        hash = bcrypt.hashpw(password.encode('utf-8'), salt)

        self.password = hash
        self.pwd_salt = salt
        db.session.commit()

    def check_password(self, password: str) -> bool:
        hash = bcrypt.hashpw(password.encode('utf-8'), self.pwd_salt)
        return hash == self.password

    def on_logged_in(self) -> None:
        self.last_signin_at = db.func.current_timestamp()
        self.signin_count += 1
        db.session.commit()


def save_new_user(email: str, password: str) -> User:
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(password.encode('utf-8'), salt)

    user = User(signin_count=1, email=email, password=hash,
                pwd_salt=salt, nickname=email[:email.find("@")])

    db.session.add(user)
    db.session.commit()
    return user


def find_user(email: str) -> User:
    return User.query.filter_by(email=email).first()


def fetch_all_users() -> list[User]:
    return User.query.all()
