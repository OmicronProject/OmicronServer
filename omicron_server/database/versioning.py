"""
Contains tools for versioning databases, and for managing database upgrades.
This code is currently not implemented in the dev version of OmicronServer,
but will eventually be used as part of the server's command line interface.

This code was adapted from Miguel Grinberg's `Flask mega-tutorial`_.

.. _Flask mega-tutorial: http://goo.gl/h5q3UP
"""
import logging
import os.path
import types

from migrate.versioning import api as sqlalchemy_migrate_api
from sqlalchemy import create_engine

from omicron_server.config import default_config as conf
from omicron_server.database.schema import metadata as meta

__author__ = 'Michal Kononenko'

log = logging.getLogger(__name__)


class DatabaseNotReferencedError(Exception):
    """
    Thrown if :class:database.versioning.DatabaseManager` is instantiated
    without an engine or a database url.
    """
    pass


class DatabaseManager(object):
    """
    Wraps methods for managing database versions. The constructor requires
    the following

    :var metadata: An object of type :class:`sqlalchemy.MetaData`, containing
        information about the database schema. Defaults to the metadata object
        located in :mod:`database.models.schema`.
    :var database_url: The URL [`RFC 3986`_] of the database to be upgraded
        or downgraded. Defaults to the database URL given in :mod:`config`,
        or read from command line environment variables.
    :var migrate_repo: An absolute path to the directory in which database
        migration scripts are stored. Defaults to the value given in
        :mod:`config`.
    :var api: The sqlalchemy-migrate API that will be used to perform the
        migration operations. This is overwritten for testability. Defaults
        to the API in :mod:`migrate.versioning`. See the Flask mega-tutorial
        for more details

    .. _RFC 3986: https://www.ietf.org/rfc/rfc3986.txt
    """
    def __init__(self, metadata=meta, database_url=None,
                 migrate_repo=conf.SQLALCHEMY_MIGRATE_REPO,
                 api=sqlalchemy_migrate_api, engine=conf.DATABASE_ENGINE):
        """
        Instantiates the variables listed above
        :raises: DatabaseNotReferencedError if the DatabaseManager is created
            without a database url or a database engine
        """
        if database_url is None and engine is None:
            raise DatabaseNotReferencedError(
                    'The manager %s was instantiated without a valid '
                    'database to work on')
        if database_url is not None:
            self.engine = create_engine(database_url)
        else:
            self.engine = engine

        self.metadata = metadata
        self.database_url = database_url
        self.migrate_repo = migrate_repo
        self.api = api

    @property
    def version(self):
        """
        Return the version of the database using the SQLAlchemy-migrate API
        """
        return self.api.db_version(self.database_url, self.migrate_repo)

    def create_db(self, engine=None):
        """
        Create a database at :attr:`self.database_url`

        :param engine: The SQLAlchemy engine which will be used to create
            the database
        """
        if engine is None:
            engine = self.engine

        self.metadata.create_all(bind=engine)

        if os.path.exists(self.migrate_repo):
            self.api.version_control(
                self.database_url, self.migrate_repo, self.version
            )
        else:
            self.api.create(self.migrate_repo)

    def create_migration_script(self):
        """
        Creates a new migration script for the database. The migration
        script is a python script located at :attr:`self.migrate_repo`. The
        target version of the script is listed on the file name. Each
        migration script must contain the following two functions.

        ``upgrade`` describes how to move from the previous version to the
        version written in the file name.

        ``downgrade`` describes how to downgrade the database from the
        version written on the file name to the previous version.

        .. warning::

            It is recommended that each migration script is reviewed prior
            to use, ESPECIALLY IN PRODUCTION. Automatically-generated
            migration scripts have known issues with migrations,
            particularly with queries involving ``ALTER COLUMN`` queries.
            In such situations, the migration script can easily ``DROP`` the
            old column and create a new one. Care should be taken when
            running migrations.
        """
        log.info(
            'Upgrading database at URL %s from version %d to %d',
            self.database_url, self.version, (self.version + 1)
        )

        migration_script_path = os.path.join(
            self.migrate_repo, '%03d_migration.py' % (self.version + 1)
        )
        temp_module = types.ModuleType('old_model')

        old_module = self.api.create_model(
            self.database_url, self.migrate_repo
        )

        eval(old_module, temp_module.__dict__)

        script = self.api.make_update_script_for_model(
            self.database_url, self.migrate_repo, temp_module.meta
        )

        with open(migration_script_path, 'wt') as migration_script:
            migration_script.write(script)

    def upgrade_db(self):
        """
        Upgrade the database to the most current version in the migrate
        repository, by running ``upgrade`` in all the migration scripts from
        the database's version up to the current version.
        """
        self.api.upgrade(self.database_url, self.migrate_repo)
        log.info('Upgraded Database %s to version %d',
                 self.database_url, self.version
                 )

    def downgrade_db(self):
        """
        Downgrade the DB from the current version to the decremented
        previous version.
        """
        old_version = self.version

        self.api.downgrade(self.database_url, self.migrate_repo,
                           (old_version - 1)
                           )

    def __repr__(self):
        """
        Returns a representation of the Database Manager useful for debugging
        :return:
        """
        return '%s(engine=%s, url=%s, migrate_repo=%s, api=%s)' % (
            self.__class__.__name__, self.engine, self.database_url,
            self.migrate_repo, self.api
        )
