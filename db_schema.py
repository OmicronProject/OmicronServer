"""
Contains the database schema to be implemented or queried, from
which models in :mod:`db_models` will be populated
"""
__author__ = 'Michal Kononenko'

from sqlalchemy import MetaData, Table, Column, Integer, String

metadata = MetaData()

user = Table(
    'users', metadata,
    Column('user_id', Integer, primary_key=True),
    Column('username', String, nullable=False),
    Column('email_address', String(64)),
    Column('password_hash', String(128), nullable=False)
    )
