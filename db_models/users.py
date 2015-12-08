"""
Contains model classes relevant to User management.
"""
from datetime import datetime, timedelta
from db_models import Base
from passlib.apps import custom_app_context as pwd_context
from sqlalchemy.orm import relationship
from config import default_config as conf
from db_schema import users, users_projects_asoc_tables, tokens
from db_models.projects import Project
from db_models.db_sessions import ContextManagedSession
from uuid import uuid1, UUID
from hashlib import sha256
from sqlalchemy import desc

__author__ = 'Michal Kononenko'


class Token(Base):
    """
    Contains methods for manipulating user tokens.
    """
    __table__ = tokens

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
    __table__ = users
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
                            secondary=users_projects_asoc_tables,
                            lazy='dynamic')

    tokens = relationship(Token, backref='owner', lazy='dynamic')

    def __init__(
            self, username, password, email,
            date_created=datetime.now()
    ):
        self.password_hash = self.hash_password(password)
        self.username = username
        self.email_address = email
        self.date_created = date_created

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

    def generate_auth_token(self,
            expiration=600,
            session=ContextManagedSession(bind=conf.DATABASE_ENGINE)):
        expiration_date = datetime.utcnow() + timedelta(seconds=expiration)

        token_string = str(uuid1())

        with session() as session:
            user = session.query(self.__class__).filter_by(
                id=self.id
            ).first()
            token = Token(token_string, expiration_date, owner=user)
            session.add(token)

        return token_string

    def verify_auth_token(self, token_string):
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
            'date_created': self.date_created.isoformat()
        }

    def __repr__(self):
        return '%s(%s, %s, %s)' % (
            self.__class__.__name__, self.username,
            self.password_hash, self.email_address
        )


class Administrator(User):
    __mapper_args__ = {
        'polymorphic_identity': True
    }