from datetime import datetime
from db_models import Base
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, \
    SignatureExpired, BadSignature
from passlib.apps import custom_app_context as pwd_context
from sqlalchemy.orm import relationship
from config import default_config as conf
from db_schema import users, users_projects_asoc_tables
from db_models.projects import Project

__author__ = 'Michal Kononenko'


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

    projects = relationship(Project, backref='members',
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
