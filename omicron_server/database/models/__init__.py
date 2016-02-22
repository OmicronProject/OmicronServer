"""
Contains database model classes. These can be loaded into and out of the
database, and are stored in persistent storage.
"""
from sqlalchemy.ext.declarative import declarative_base

from omicron_server.database import schema

__author__ = 'Michal Kononenko'

Base = declarative_base(metadata=schema.metadata)