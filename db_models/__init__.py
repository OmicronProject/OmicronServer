from sqlalchemy.ext.declarative import declarative_base
import db_schema

__author__ = 'Michal Kononenko'

Base = declarative_base(metadata=db_schema.metadata)