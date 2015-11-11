"""
Contains global config parameters for the API
"""
import os
from sqlalchemy import create_engine
import sys
import logging

log = logging.getLogger(__name__)

if sys.version_info < (3,):
    import ConfigParser as configparser # Python 2 compatibility
else:
    import configparser

__author__ = 'Michal Kononenko'


class Config(object):
    """
    Contains configuration parameters and methods for broadcasting config
    changes to ``alembic.ini`` and receiving changes from environment variables.

    For global configuration, system environment variables have priority,
    followed by values in this object, then followed by the value
    in a component's configuration file
    """
    STATE = 'DEV'
    VERSION = '0.1.1'
    DEBUG = True

    BASE_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
    JSON_SCHEMA_PATH = os.path.join(BASE_DIRECTORY, 'schemas')

    DATABASE_URL = 'sqlite:///%s' % ('test_db.sqlite3')
    DATABASE_ENGINE = create_engine(DATABASE_URL)

    SQLALCHEMY_MIGRATE_REPO = os.path.join(BASE_DIRECTORY, 'db_versioning_repo')

    IP_ADDRESS = '127.0.0.1'
    PORT = 5000
    TOKEN_SECRET_KEY = 'rKrafg2L1HozC7jg1GvaXPZoHa32MiX51'

    ENVIRONMENT_VARIABLES = [
        'BASE_DIRECTORY', 'PORT',
        'DATABASE_URL', 'TOKEN_SECRET_KEY',
        'DEBUG', 'STATE', 'IP_ADDRESS'
    ]

    def __init__(self, conf_dict=os.environ):
        for key in self.ENVIRONMENT_VARIABLES:
            try:
                value = conf_dict[key]
            except KeyError:
                value = getattr(self, key)
                log.info(
                    'Environment variable %s not supplied, '
                    'using default value of %s',
                    key, value
                )
            if key == 'PORT':
                value = int(value)

            self.__dict__[key] = value

default_config = Config()
