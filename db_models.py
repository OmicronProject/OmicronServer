"""
Contains the SQLAlchemy ORM model for the API
"""
__author__ = 'Michal Kononenko'

from sqlalchemy.ext.declarative import declarative_base
from db_schema import metadata, user

Base = declarative_base(metadata=metadata)


class User(Base):
    __table__ = user

    id = __table__.user_id
    username = __table__.username
    email_address =  __table__.email_address
    password_hash = __table__.password_hash