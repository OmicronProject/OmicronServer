from migrate.versioning import api as sqlalchemy_migrate_api
from config import default_config as conf
import os.path
import logging
from db_schema import metadata as meta
from sqlalchemy import create_engine
import types

__author__ = 'Michal Kononenko'

log = logging.getLogger(__name__)


class DatabaseManager(object):
    """
    Contains methods for upgrading, downgrading, and migrating databases on
    schema change
    """
    def __init__(self, metadata=meta, database_url=conf.DATABASE_URL,
                 migrate_repo=conf.SQLALCHEMY_MIGRATE_REPO,
                 api=sqlalchemy_migrate_api):
        self.metadata = metadata
        self.database_url = database_url
        self.migrate_repo = migrate_repo
        self.api = api

        self._default_engine = None

    @property
    def default_engine(self):
        if self._default_engine is None:
            self._default_engine = create_engine(self.database_url)
        return self._default_engine

    @property
    def version(self):
        """
        Return the version of the database using a SQLAlchemy-migrate API
        """
        return self.api.db_version(self.database_url, self.migrate_repo)

    def create_db(self, engine=None):
        """
        Create a database at :attr:`self.database_url`

        :param engine: The SQLAlchemy engine which will be used to create
        """
        if engine is None:
            engine = self.default_engine

        self.metadata.create_all(bind=engine)

        if not os.path.exists(self.migrate_repo):
            self.api.create(self.migrate_repo)
        else:
            self.api.version_control(
                self.database_url, self.migrate_repo, self.version
            )

    def migrate_db(self):
        log.info('Upgrading database at URL %s from version %d to %d',
                 self.database_url, self.version, (self.version + 1)
        )

        migration_script_path = os.path.join(
            self.migrate_repo, '%03d_migration.py' % (self.version + 1)
        )

        temp_module = types.ModuleType('old_model')

        old_module = self.api.create_model(
            self.database_url, self.migrate_repo
        )

        exec(old_module, temp_module.__dict__)

        script = self.api.make_update_script_for_model(
            self.database_url, self.migrate_repo, temp_module.meta
        )

        with open(migration_script_path, 'wt') as migration_script:
            migration_script.write(script)

        self.api.upgrade(self.database_url, self.migrate_repo)

        log.info('Database at URL %s upgraded to version %d',
                 self.database_url, self.version
                 )

    def upgrade_db(self):
        self.api.upgrade(self.database_url, self.migrate_repo)
        log.info('Upgraded Database %s to version %d',
                 self.database_url, self.version
        )

    def downgrade_db(self):
        old_version = self.version

        self.api.downgrade(self.database_url, self.migrate_repo,
                           (old_version - 1)
        )