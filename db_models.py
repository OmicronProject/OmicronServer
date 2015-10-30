"""
Contains the SQLAlchemy ORM model for the API
"""
__author__ = 'Michal Kononenko'

from sqlalchemy.ext.declarative import declarative_base
from db_schema import metadata, user
from passlib.apps import custom_app_context as pwd_context
from sqlalchemy import create_engine
from config import DATABASE_URI
from sqlalchemy.orm import sessionmaker as sqlalchemy_sessionmaker

Base = declarative_base(metadata=metadata)

sqlalchemy_engine = create_engine(DATABASE_URI)


def sessionmaker(engine=None):
    """
    Overwrites the factory :func:`sqlalchemy.create_engine` in order
    to avoid having to specify ``bind=sqlalchemy_engine`` with every call to
    SQLAlchemy's session factory
    :param engine engine: The SQLAlchemy engine to which this session is to be
        bound. If not specified, will bind to the default engine given by
        :attr:`config.DATABASE_URI`
    :return:
    """
    return sqlalchemy_sessionmaker(bind=engine) if engine is not None \
        else sqlalchemy_sessionmaker(bind=sqlalchemy_engine)


class User(Base):
    """
    Base class for a user
    """
    __table__ = user
    __columns__ = __table__.c

    id = __columns__.user_id
    username = __columns__.username
    email_address = __columns__.email_address
    password_hash = __columns__.password_hash

    def __init__(self, username, email, password):
        self.hash_password(password)
        self.username = username
        self.email = email

    def hash_password(self, password):
        """
        Hash the user's password
        :param str password: The password to hash
        :return:
        """
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        """
        Verify the user's password
        :param str password: The password to verify
        :return: True if the password is correct, else False
        :rtype: bool
        """
        return pwd_context.verify(password, self.password_hash)