"""
Contains global config parameters for the API
"""
import os
from sqlalchemy import create_engine

__author__ = 'Michal Kononenko'


STATE = 'DEV'

BASE_DIRECTORY = os.path.abspath(os.path.dirname(__file__))

try:
	if os.environ['DATABASE_URL'] is not None:
		DATABASE_URI = os.environ['DATABASE_URL']
except KeyError:
	DATABASE_URI = 'sqlite:///' + os.path.join(
		BASE_DIRECTORY, 'test_db.sqlite3'
	)

# DATABASE_URI = 'postgresql://localhost:5432/OmicronAPITestDB' # Postgres database

DATABASE_MIGRATE_REPO = os.path.join(
    BASE_DIRECTORY, 'db_migrations'
)

JSON_SCHEMA_PATH = os.path.join(BASE_DIRECTORY, 'schemas')

TOKEN_SECRET_KEY = 'rKrafg2L1HozC7jg1GvaXPZoHa32MiX51'

DATABASE_ENGINE = create_engine(DATABASE_URI)


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
