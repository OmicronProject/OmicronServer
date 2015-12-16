"""
Contains persistent model classes in the database.
"""
from sqlalchemy.ext.declarative import declarative_base

from database import schema

__author__ = 'Michal Kononenko'

Base = declarative_base(metadata=schema.metadata)