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

    DATABASE_URL = 'sqlite:///'
    DATABASE_ENGINE = create_engine(DATABASE_URL)

    PORT = 5000
    TOKEN_SECRET_KEY = 'rKrafg2L1HozC7jg1GvaXPZoHa32MiX51'

    TEMPLATE_ALEMBIC_INI_PATH = os.path.join(
        BASE_DIRECTORY, 'static', 'alembic.ini'
    )
    ALEMBIC_CONF_FILE = os.path.join(BASE_DIRECTORY, 'alembic.ini')

    ENVIRONMENT_VARIABLES = [
        'BASE_DIRECTORY', 'PORT',
        'DATABASE_URL', 'TOKEN_SECRET_KEY',
        'DEBUG', 'STATE'
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

        self.update_alembic_ini(
            self.DATABASE_URL, self.TEMPLATE_ALEMBIC_INI_PATH,
            self.ALEMBIC_CONF_FILE
        )

    @staticmethod
    def update_alembic_ini(
            database_url, static_alembic_conf, alembic_conf_path
    ):
        config = configparser.ConfigParser()
        config.read(static_alembic_conf)

        if sys.version_info < (3,): # Using Python2
            Config._update_python2(config, database_url, alembic_conf_path)
        else:
            Config._update_python3(config, database_url, alembic_conf_path)

    @staticmethod
    def _update_python2(parsed_config, database_url, alembic_conf_path):
        parsed_config.set('alembic', 'sqlalchemy.url', database_url)
        with open(alembic_conf_path, 'w') as configfile:
            parsed_config.write(configfile)

    @staticmethod
    def _update_python3(parsed_config, database_url, alembic_conf_path):
        parsed_config['alembic']['sqlalchemy.url'] = database_url

        with open(alembic_conf_path, 'w') as configfile:
            parsed_config.write(configfile)

default_config = Config()
