"""
Contains the database schema to be implemented or queried, from
which models in :mod:`db_models` will be populated
"""
from sqlalchemy import MetaData, Table, Column, Integer, String, Boolean
__author__ = 'Michal Kononenko'

metadata = MetaData()

users = Table(
    'users', metadata,
    Column('user_id', Integer, primary_key=True),
    Column('username', String, nullable=False),
    Column('email_address', String(64)),
    Column('password_hash', String(128), nullable=False),
    Column('is_superuser', Boolean, nullable=False, default=False)
    )
