"""
Contains the base class from which the model classes inherit.
The model classes have representations in the database provided by
SQLAlchemy, as well as JSON Schemas that can be used to serialize
and deserialize these objects with marshmallow.
"""
from database import schema
from sqlalchemy.ext.declarative import declarative_base

__author__ = 'Michal Kononenko'

__all__ = ["Base"]

Base = declarative_base(metadata=schema.metadata)
