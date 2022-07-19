from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import bcrypt
import string
import random
from datetime import date, timedelta
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.orm import query_expression, with_expression
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.collections import attribute_mapped_collection


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime,
                           server_default=db.func.current_timestamp(),
                           nullable=False)
    signin_count = query_expression()
    last_signin_at = query_expression()
    email = db.Column(db.String(255), unique=True, nullable=False)
    nickname = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=True)
    pwd_salt = db.Column(db.String(255), nullable=True)
    activation_key = db.Column(db.String(255), nullable=True)
    activated_at = db.Column(db.DateTime, nullable=True)
    sessions = db.relationship(
        "UserSession",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )
    oauths = db.relationship(
        "OAuth",
        back_populates="user",
        collection_class=attribute_mapped_collection("provider"),
        cascade="all, delete",
        passive_deletes=True,
    )

    def __repr__(self):
        return f"User({self.id}, '{self.nickname}', '{self.email}')"

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
        if self.password is None:
            return password is None
        hash = bcrypt.hashpw(password.encode('utf-8'), self.pwd_salt)
        return hash == self.password

    def on_logged_in(self) -> None:
        self.add_session()

        db.session.commit()

    def activate(self, key: str) -> bool:
        if key != self.activation_key:
            return False

        self.activated_at = db.func.current_timestamp()
        self.activation_key = None

        self.add_session()

        db.session.commit()
        return True

    def update_nickname(self, nickname: str) -> None:
        self.nickname = nickname

        db.session.commit()

    def add_session(self) -> None:
        user_session = UserSession(logged_at=db.func.current_timestamp())
        self.sessions.append(user_session)

    def link_oauth(self, oauth: 'OAuth') -> None:
        if self.activated_at is None:
            self.activated_at = db.func.current_timestamp()

        oauth.user = self

        self.add_session()

        db.session.add_all([self, oauth])
        db.session.commit()

    @staticmethod
    def __generate_random_string(length: int) -> str:
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    @staticmethod
    def Create(email: str, password: str) -> 'User':
        salt = bcrypt.gensalt()
        hash = bcrypt.hashpw(password.encode('utf-8'), salt)

        user = User(email=email, password=hash, pwd_salt=salt,
                    nickname=email[:email.find("@")])

        user.activation_key = User.__generate_random_string(50)

        user.add_session()

        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def CreateWithOAuth(email: str, nickname: str, oauth: 'OAuth') -> 'User':
        user = User(email=email, nickname=nickname,
                    activated_at=db.func.current_timestamp())

        # Associate the new local user account with the OAuth token
        oauth.user = user

        user.add_session()

        db.session.add_all([user, oauth])
        db.session.commit()
        return user

    @staticmethod
    def FindById(id: int) -> 'User':
        return User.query.get(id)

    @staticmethod
    def FindByEmail(email: str) -> 'User':
        return User.query.filter_by(email=email).first()

    @staticmethod
    def FetchAll() -> list['User']:
        return db.session.query(User).options(
            with_expression(User.signin_count, db.func.count(UserSession.id))
            .with_expression(User.last_signin_at, db.func.max(UserSession.logged_at))) \
            .join(UserSession, User.id == UserSession.user_id) \
            .group_by(User.id) \
            .all()

    @staticmethod
    def GetStatistics() -> dict:
        # Total number of users who have signed up
        # Total number of users with active sessions today
        total_active_today_query = db.session.query(db.func.count(db.distinct(UserSession.user_id))) \
            .select_from(UserSession) \
            .filter(db.func.date(UserSession.logged_at) == date.today())

        total_users, total_active_today = db.session.query(
            db.func.count(User.id).label('total_users'),
            total_active_today_query.label('total_active_today')) \
            .select_from(User) \
            .first()

        # Average number of active session users in the last 7 days
        nb_last_days = 7
        end_date = date.today()
        start_date = end_date - timedelta(days=nb_last_days - 1)

        logged_date = db.func.date(UserSession.logged_at).label('logged_date')
        count = db.func.count(UserSession.id).label('count')

        q = db.session.query(logged_date, count) \
            .select_from(UserSession) \
            .filter(db.text(f"{logged_date.name} BETWEEN '{start_date}' AND '{end_date}'")) \
            .group_by(logged_date.name, UserSession.user_id)

        sum = db.session.query(db.func.sum(db.text(count.name))) \
            .select_from(q).first()[0]

        return {
            'total_users': total_users,
            'total_active_today': total_active_today,
            'avg_last_days': sum / nb_last_days
        }


class UserSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,
                        db.ForeignKey(User.id, ondelete="CASCADE"),
                        nullable=False)
    user = db.relationship(User, back_populates="sessions")
    logged_at = db.Column(db.DateTime,
                          server_default=db.func.current_timestamp(),
                          nullable=False)


class OAuth(OAuthConsumerMixin, db.Model):
    provider_user_id = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer,
                        db.ForeignKey(User.id, ondelete="CASCADE"),
                        nullable=False)
    user = db.relationship(User, back_populates="oauths")
    __table_args__ = (db.UniqueConstraint('provider', 'provider_user_id'), )

    @staticmethod
    def FindUser(provider: str, user_id: int) -> User:
        query = OAuth.query.filter_by(
            provider=provider, provider_user_id=user_id)

        try:
            return query.one().user
        except NoResultFound:
            return None

    @staticmethod
    def Create(provider: str, user_id: int, token: str) -> 'OAuth':
        return OAuth(provider=provider,
                     provider_user_id=user_id, token=token)
