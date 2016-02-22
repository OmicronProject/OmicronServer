"""
Contains all model classes relevant to management of users
"""
from datetime import datetime, timedelta
from hashlib import sha256
from uuid import uuid1, UUID

from database.models import Base
from database.models.projects import Project
from database.sessions import ContextManagedSession
from passlib.apps import custom_app_context as pwd_context
from sqlalchemy import desc
from sqlalchemy.orm import relationship

from omicron_server.config import default_config as conf
from omicron_server.database import schema

__author__ = 'Michal Kononenko'


class Token(Base):
    """
    Contains methods for manipulating user tokens.
    """
    __table__ = schema.tokens

    token_hash = __table__.c.token_hash
    date_created = __table__.c.date_created
    expiration_date = __table__.c.expiration_date

    def __init__(
            self, token_string, expiration_date=None, owner=None
    ):
        if isinstance(token_string, UUID):
            token_string = str(token_string)

        self.date_created = datetime.utcnow()
        self.token_hash = self.hash_token(token_string)

        if expiration_date is None:
            expiration_date = self.date_created + timedelta(
                seconds=conf.DEFAULT_TOKEN_EXPIRATION_TIME)

        self.expiration_date = expiration_date
        self.owner = owner

    @staticmethod
    def hash_token(token_string):
        """
        Takes a token string and hashes it using SHA256.
        """
        return sha256(token_string.encode('ascii')).hexdigest()

    def verify_token(self, token):
        """
        Checks if the provided token string matches the token hash in the DB,
        and that the token is not expired
        :param str token: The token to verify
        :return: True if the token is valid, False if not
        """
        if datetime.utcnow() > self.expiration_date:
            return False

        return self.hash_token(token) == self.token_hash

    def revoke(self):
        """
        Expire the token by setting the expiration date equal to the current
        date
        """
        self.expiration_date = datetime.utcnow()


class User(Base):
    """
    Base class for a User.
    """
    __table__ = schema.users
    __columns__ = __table__.c

    id = __columns__.user_id
    username = __columns__.username
    email_address = __columns__.email_address
    password_hash = __columns__.password_hash
    date_created = __columns__.date_created

    __mapper_args__ = {
        'polymorphic_identity': False,
        'polymorphic_on': __table__.c.is_superuser
    }

    projects = relationship(Project, backref='members',
                            secondary=schema.users_projects_asoc_tables,
                            lazy='dynamic')

    owned_projects = relationship(Project, backref='owner',
                                  foreign_keys=schema.projects.c.owner_id)

    tokens = relationship(Token, backref='owner', lazy='dynamic')

    def __init__(
            self, username, password, email,
            date_created=datetime.now()
    ):
        self.password_hash = self.hash_password(password)
        self.username = username
        self.email_address = email
        self.date_created = date_created

    @classmethod
    def from_session(cls, username, session):
        """
        Provides an alternate "constructor" by using the supplied
        session and returning the user matching the given username.
        The method also asserts that a user was returned by the query.
        If it did not happen, something horrible has happened.

        :param str username: The username of the user to get
        :param ContextManagedSession session: The session to use for retrieving
            the user
        :return: The user to be retrieved
        """
        user = session.query(cls).filter_by(username=username).first()
        if not isinstance(user, cls):
            raise TypeError(
                'The returned user of type %s is not of expected type %s',
                user.__class__.__name__, cls.__name__
            )
        return user

    @staticmethod
    def hash_password(password):
        """
        Hash the user's password
        :param str password: The password to hash
        :return:
        """
        return pwd_context.encrypt(password)

    def verify_password(self, password):
        """
        Verify the user's password
        :param str password: The password to verify
        :return: True if the password is correct, else False
        :rtype: bool
        """
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(
            self, expiration=conf.DEFAULT_TOKEN_EXPIRATION_TIME,
            session=ContextManagedSession(bind=conf.DATABASE_ENGINE)
    ):
        """
        Generates a token for the user. The user's token is a `UUID 1`_,
        randomly generated in this function. A :class:`Token` is created
        with this randomly-generated UUID, the UUID token is hashed,
        and stored in the database.

            .. warning::

                The string representation of the generated token is returned
                only once, and is not recoverable from the data stored in the
                database. The returned token is also a proxy for the user's
                password, so treat it as such.

        :param int expiration: The lifetime of the token in seconds.
        :param ContextManagedSession session: The database session with
            which this method will interact, in order to produce a token. By
            default, this is a :class:`ContextManagedSession` that will
            point to :attr:`conf.DATABASE_ENGINE`, but for the purposes of unit
            testing, it can be repointed.
        :return: A tuple containing the newly-created authentication token,
            and the expiration date of the new token. The expiration date
            is an object of type :class:`Datetime`
        :rtype: tuple(str, Datetime)

        .. _UUID 1: https://goo.gl/iUS6s9
        """
        expiration_date = datetime.utcnow() + timedelta(seconds=expiration)

        token_string = str(uuid1())

        with session() as session:
            user = session.query(self.__class__).filter_by(
                id=self.id
            ).first()
            token = Token(token_string, expiration_date, owner=user)
            session.add(token)

        return token_string, expiration_date

    def verify_auth_token(self, token_string):
        """
        Loads the user's current token, and uses that token to check whether
        the supplied token string is correct

        :param str token_string: The token to validate
        :return: ``True`` if the token is valid and ``False`` if not
        """
        token = self.current_token

        return token.verify_token(token_string)

    @property
    def current_token(self):
        return self.tokens.order_by(desc(Token.date_created))

    @property
    def get(self):
        return {'username': self.username, 'email': self.email_address,
                'date_created': self.date_created.isoformat()}

    @property
    def get_full(self):
        return {
            'username': self.username,
            'email': self.email_address,
            'date_created': self.date_created.isoformat(),
            'projects': [project.get_full for project in self.projects.all()]
        }

    def __repr__(self):
        return '%s(%s, %s, %s)' % (
            self.__class__.__name__, self.username,
            self.password_hash, self.email_address
        )

    def __eq__(self, other):
        """
        :param User other: The user against which to compare
        """
        return self.username == other.username

    def __ne__(self, other):
        """
        Check if two users are not equal
        :param other:
        """
        return self.username != other.username


class Administrator(User):
    """
    Represents a "superuser" type. The administrator will be able to oversee
    all projects, revoke anyone's token, and approve new users into the system,
    when user approval is complete.
    """
    __mapper_args__ = {
        'polymorphic_identity': True
    }
