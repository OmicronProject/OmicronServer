"""
Contains the SQLAlchemy ORM model for the API
"""
from sqlalchemy.ext.declarative import declarative_base
from db_schema import metadata, user
from passlib.apps import custom_app_context as pwd_context
from sqlalchemy import create_engine
from config import DATABASE_URI, TOKEN_SECRET_KEY
from sqlalchemy.orm import sessionmaker as sqlalchemy_sessionmaker
from sqlalchemy.orm import Session
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, \
    BadSignature, SignatureExpired

__author__ = 'Michal Kononenko'

Base = declarative_base(metadata=metadata)


class ContextManagedSession(Session):
    """
    An extension to :cls:`sqlalchemy.orm.Session` that allows the session
    to be run using a ``with`` statement, committing all changes on an
    error-free exit from the context manager
    """

    def __enter__(self):
        session = self.__class__()
        session.__dict__ = self.__dict__
        return session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            try:
                self.commit()
            except:
                self.rollback()
                raise
        else:
            self.rollback()
            raise exc_val

    def __repr__(self):
        return '%s(bind=%s, expire_on_commit=%s)' % \
               (self.__class__.__name__, self.bind, self.expire_on_commit)


def sessionmaker(engine=None):
    """
    Overwrites the factory :func:`sqlalchemy.orm.sessionmaker` in order
    to avoid having to specify ``bind=sqlalchemy_engine`` with every call to
    SQLAlchemy's session factory
    :param engine engine: The SQLAlchemy engine to which this session is to be
        bound. If not specified, will bind to the default engine given by
        :attr:`config.DATABASE_URI`
    :return:
    """
    if engine is None:
        engine = create_engine(DATABASE_URI)
    return ContextManagedSession(bind=engine)


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

    def __init__(self, username, password, email):
        self.password_hash = self.hash_password(password)
        self.username = username
        self.email = email

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

    def generate_auth_token(self, expiration=600):
        s = Serializer(TOKEN_SECRET_KEY, expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(TOKEN_SECRET_KEY)
        try:
            data = s.loads(token)
        except (SignatureExpired, BadSignature):
            return None
        else:
            return data['id']
