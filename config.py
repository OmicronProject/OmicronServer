"""
Contains global config parameters for the API
"""
import os

__author__ = 'Michal Kononenko'


STATE = 'DEV'

BASE_DIRECTORY = os.path.abspath(os.path.dirname(__file__))

DATABASE_URI = 'sqlite:///' + os.path.join(
    BASE_DIRECTORY, 'test_db.sqlite3'
)

DATABASE_MIGRATE_REPO = os.path.join(
    BASE_DIRECTORY, 'db_migrations'
)

JSON_SCHEMA_PATH = os.path.join(BASE_DIRECTORY, 'schemas')

if STATE == 'DEV':
    DEBUG = True
    PORT = 5000
elif STATE == 'CI':
    DEBUG = True
    PORT = 5000
else:
    STATE = 'PROD'
    DEBUG = 'FALSE'
    PORT = 5000
