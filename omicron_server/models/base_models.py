from sqlalchemy.ext.declarative import declarative_base
from omicron_server.database import schema

__author__ = 'Michal Kononenko'

Base = declarative_base(metadata=schema.metadata)
