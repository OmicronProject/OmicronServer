import unittest
import mock
import logging
from db_schema import metadata as meta
import db_versioning as dbv
import sys

__author__ = 'Michal Kononenko'

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

if sys.version_info < (3,):
    builtin_string = '__builtin__'
else:
    builtin_string = 'builtins'


class MockMigrateAPI(mock.MagicMock):

    _version = 1

    def db_version(self, db_url, migrate_repo):
        return self._version, mock.call(db_url, migrate_repo)


class MockModule(mock.MagicMock):
    meta = 2


class TestDatabaseManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.metadata = mock.MagicMock()
        cls.database_url = 'sqlite:///'
        cls.migrate_repo = 'test_directory'
        cls.api = MockMigrateAPI()

        cls.manager = dbv.DatabaseManager(
            metadata=cls.metadata, database_url=cls.database_url,
            migrate_repo=cls.migrate_repo, api=cls.api
        )


class TestDatabaseManagerConstructor(unittest.TestCase):

    def setUp(self):
        self.metadata = meta
        self.database_url = 'sqlite:///'
        self.migrate_repo = 'test_directory'
        self.api = MockMigrateAPI()

    def test_constructor(self):
        manager = dbv.DatabaseManager(
            metadata=self.metadata, database_url=self.database_url,
            migrate_repo=self.migrate_repo, api=self.api
        )

        self.assertIsInstance(manager, dbv.DatabaseManager)
        self.assertEqual(manager.api, self.api)


class TestDatabaseManagerDefaultEngine(TestDatabaseManager):

    @mock.patch('db_versioning.create_engine')
    def test_default_engine_none(self, mock_create_engine):
        mock_engine_call = mock.call(self.database_url)
        self.manager._default_engine = None

        engine = self.manager.default_engine

        self.assertIsInstance(engine, mock.MagicMock)
        self.assertEqual(mock_engine_call, mock_create_engine.call_args)

    def test_default_engine_is_not_none(self):
        engine = mock.MagicMock()
        self.manager._default_engine = engine
        self.assertEqual(self.manager.default_engine, engine)


class TestManagerVersion(TestDatabaseManager):
    def setUp(self):
        TestDatabaseManager.setUp(self)
        self.version = 1
        self.api._version = self.version

    def test_version(self):
        self.assertEqual(self.version, self.manager.version[0])
        self.assertEqual(mock.call(self.database_url, self.migrate_repo),
                         self.manager.version[1]
                         )


class TestCreateDB(TestDatabaseManager):
    def setUp(self):
        self.manager.metadata = mock.MagicMock()
        self.manager._default_engine = mock.MagicMock()

    @mock.patch('os.path.exists', return_value=False)
    def test_create_db_no_engine(self, mock_path_exists):
        """
        Test that the DB creates an engine pointing to the default database
        URL if an engine isn't provided on construction
        """
        self.manager.create_db()

        self.assertTrue(mock_path_exists.called)

        self.assertEqual(
            self.manager.metadata.create_all.call_args,
            mock.call(bind=self.manager.default_engine)
        )

    @mock.patch('os.path.exists', return_value=True)
    def test_create_db_version_control(self, mock_os_exists):
        self.manager.engine = mock.MagicMock()

        mock_version_call = mock.call(
            self.manager.database_url, self.manager.migrate_repo,
            self.manager.version
        )

        self.manager.create_db()

        self.assertEqual(
            self.manager.api.version_control.call_args,
            mock_version_call
        )

        self.assertTrue(mock_os_exists.called)


class TestCreateMigrationScript(TestDatabaseManager):
    def setUp(self):
        TestDatabaseManager.setUp(self)
        self.manager.api.db_version = mock.MagicMock(new=1)

    @mock.patch('%s.exec' % builtin_string)
    @mock.patch('%s.open' % builtin_string)
    @mock.patch('db_versioning.types.ModuleType', return_value=MockModule())
    def test_migrate_db(self, mock_module, mock_open, mock_exec):
        self.manager.create_migration_script()

        self.assertTrue(mock_exec.called)
        self.assertTrue(mock_open.called)
        self.assertTrue(mock_module.called)


class TestUpgradeDB(TestDatabaseManager):
    def setUp(self):
        TestDatabaseManager.setUp(self)
        self.manager.api.db_version = \
            mock.MagicMock(return_value=1)

        self.mock_upgrade_call = mock.call(
            self.manager.database_url, self.manager.migrate_repo
        )

    def test_upgrade_db(self):
        self.manager.upgrade_db()

        self.assertEqual(
            self.manager.api.upgrade.call_args, self.mock_upgrade_call
        )


class TestDowngradeDB(TestDatabaseManager):
    def setUp(self):
        TestDatabaseManager.setUp(self)

        self.manager.api.db_version = mock.MagicMock(return_value=1)

        self.mock_downgrade_call = mock.call(
            self.manager.database_url, self.manager.migrate_repo,
            (self.manager.version - 1)
        )

    def test_downgrade_db(self):

        self.manager.downgrade_db()

        self.assertEqual(
            self.manager.api.downgrade.call_args, self.mock_downgrade_call
        )