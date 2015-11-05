"""
Contains global config parameters for the API
"""
import os
from sqlalchemy import create_engine
import sys

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

    DATABASE_URL = 'sqlite:///'
    DATABASE_ENGINE = create_engine(DATABASE_URL)

    PORT = 5000
    TOKEN_SECRET_KEY = 'rKrafg2L1HozC7jg1GvaXPZoHa32MiX51'

    ALEMBIC_CONF_FILE = os.path.join(BASE_DIRECTORY, 'alembic.ini')

    ENVIRONMENT_VARIABLES = [
        'BASE_DIRECTORY', 'PORT',
        'DATABASE_URL', 'TOKEN_SECRET_KEY',
        'DEBUG', 'STATE'
    ]

    def __init__(self, conf_dict=os.environ):
        for attribute in self.ENVIRONMENT_VARIABLES:
            try:
                self.__dict__[attribute] = conf_dict[attribute]
            except KeyError:
                pass

        self.update_alembic_ini(self.DATABASE_URL, self.ALEMBIC_CONF_FILE)

    @staticmethod
    def update_alembic_ini(database_url, alembic_conf_path):
        config = configparser.ConfigParser()
        config.read(alembic_conf_path)

        config['alembic']['sqlalchemy.url'] = database_url

        with open(alembic_conf_path, 'w') as configfile:
            config.write(configfile)

default_config = Config()
