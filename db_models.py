"""
Contains the SQLAlchemy ORM model for the API
"""
from sqlalchemy.ext.declarative import declarative_base
from db_schema import metadata, users, users_projects_asoc_tables, projects
from passlib.apps import custom_app_context as pwd_context
from config import default_config as conf
from sqlalchemy.orm import Session, relationship
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, \
    BadSignature, SignatureExpired
import logging
from datetime import datetime


__author__ = 'Michal Kononenko'
log = logging.getLogger(__name__)

Base = declarative_base(metadata=metadata)


class NotDecoratableError(ValueError):
    pass


class ContextManagedSession(Session):
    """
    An extension to :class:`sqlalchemy.orm.Session` that allows the session
    to be run using a ``with`` statement, committing all changes on an
    error-free exit from the context manager
    """

    def copy(self):
        """
        Returns a new :class:`ContextManagedSession` with the same namespace
        as ``self``
        """
        session = self.__class__()
        session.__dict__ = self.__dict__
        return session

    def __call__(self, f=None):
        if hasattr(f, '__call__'):
            return self._decorator(f)
        else:
            return self

    def _decorator(self, f):
        def _wrapped_function(*args, **kwargs):
            with self as session:
                response = f(session, *args, **kwargs)
            return response

        _wrapped_function.__name__ = f.__name__
        _wrapped_function.__doc__ = f.__doc__
        return _wrapped_function

    def __enter__(self):
        return self.copy()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            try:
                self.commit()
            except BaseException as exc:
                log.error('Session commit raised error %s', exc)
                self.rollback()
                raise exc
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
    :return: A new database session
    :rtype: :class:`db_models.ContextManagedSession`
    """
    return ContextManagedSession(bind=engine)


class User(Base):
    """
    Base class for a user.
    """
    __table__ = users
    __columns__ = __table__.c

    id = __columns__.user_id
    username = __columns__.username
    email_address = __columns__.email_address
    password_hash = __columns__.password_hash
    date_created = __columns__.date_created

    projects = relationship('Project', backref='members',
                            secondary=users_projects_asoc_tables,
                            lazy='dynamic')

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

    def generate_auth_token(self, expiration=600):
        s = Serializer(conf.TOKEN_SECRET_KEY, expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(conf.TOKEN_SECRET_KEY)
        try:
            data = s.loads(token)
        except (SignatureExpired, BadSignature):
            return None
        else:
            return data['id']

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


class Project(Base):
    """
    Models a project for a given user. The project constructor requires
    the following

    :var str project_name: The name of the project
    :var str description: A description of the project

    """
    __table__ = projects

    id = __table__.c.project_id
    name = __table__.c.name
    description = __table__.c.description
    date_created = __table__.c.date_created

    def __init__(
        self, project_name, description,
        date_created=datetime.utcnow(),
        owner=None
    ):
        self.name = project_name
        self.date_created = date_created
        self.owner = owner
        self.description = description

    @property
    def date_created_isoformat(self):
        return self.date_created.isoformat()
