"""
Contains unit tests for :mod:`database.versioning`
"""
import logging
import sys
import unittest

import mock
from omicron_server.database import DatabaseManager
from omicron_server.database.versioning import DatabaseNotReferencedError
from sqlalchemy import create_engine

from omicron_server.database.schema import metadata as meta

__author__ = 'Michal Kononenko'

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

builtin_string = '__builtin__' if sys.version_info < (3,) else 'builtins'


class MockMigrateAPI(mock.MagicMock):
    """
    Designed to replicate the functionality of the sqlalchemy-migrate API in
    order to perform testing
    """
    _version = 1

    def db_version(self, db_url, migrate_repo):
        return self._version, mock.call(db_url, migrate_repo)


class MockModule(mock.MagicMock):
    meta = 2


class TestDatabaseManager(unittest.TestCase):
    """
    Base test for :class:`database.versioning.DatabaseManager`
    """
    @classmethod
    def setUpClass(cls):
        """
        Set up unit test
        """
        cls.metadata = mock.MagicMock()
        cls.database_url = 'sqlite:///'
        cls.migrate_repo = 'test_directory'
        cls.api = MockMigrateAPI()

        cls.manager = DatabaseManager(
            metadata=cls.metadata, database_url=cls.database_url,
            migrate_repo=cls.migrate_repo, api=cls.api
        )


class TestDatabaseManagerConstructor(unittest.TestCase):
    """
    Contains unit tests for
    :meth:`database.versioning.DatabaseManager.__init__`
    """
    def setUp(self):
        self.metadata = meta
        self.database_url = 'sqlite:///'
        self.migrate_repo = 'test_directory'
        self.api = MockMigrateAPI()
        self.engine = create_engine(self.database_url)

    def test_constructor_no_engine(self):
        """
        Tests that the constructor is capable of creating a proper
        :class:`database.versioning.DatabaseManager`, mapping provided
        database URLs, migrate repos, and APIs to their respective attributes
        """
        manager = DatabaseManager(
            metadata=self.metadata, database_url=self.database_url,
            migrate_repo=self.migrate_repo, api=self.api
        )

        self.assertIsInstance(manager, DatabaseManager)
        self.assertEqual(manager.api, self.api)
        self.assertEqual(manager.migrate_repo, self.migrate_repo)
        self.assertEqual(manager.database_url, self.database_url)

    def test_constructor_with_engine(self):
        """
        Tests that the constructor ignores database URLs when an engine is
        provided
        """
        manager = DatabaseManager(
            metadata=self.metadata, migrate_repo=self.migrate_repo,
            engine=self.engine
        )
        self.assertIsNone(manager.database_url)
        self.assertEqual(manager.engine, self.engine)

    def test_constructor_no_reference_error(self):
        """
        Tests that the constructor throws an
        :exc:`database.versioning.DatabaseNotReferencedError` if a
        ``database_url`` and ``engine`` are not supplied.
        """
        with self.assertRaises(DatabaseNotReferencedError):
            DatabaseManager(
                metadata=self.metadata, migrate_repo=self.migrate_repo,
                engine=None, database_url=None
            )


class TestManagerVersion(TestDatabaseManager):
    """
    Tests :meth:`database.versioning.DatabaseManager.version`
    """
    def setUp(self):
        TestDatabaseManager.setUp(self)
        self.version = 1
        self.api._version = self.version

    def test_version(self):
        """
        Tests the property
        """
        self.assertEqual(self.version, self.manager.version[0])
        self.assertEqual(mock.call(self.database_url, self.migrate_repo),
                         self.manager.version[1]
                         )


class TestCreateDB(TestDatabaseManager):
    """
    Contains unit tests for
    :meth:`database.versioning.DatabaseManager.create_db`
    """
    def setUp(self):
        self.manager.metadata = mock.MagicMock()
        self.manager.engine = mock.MagicMock()

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
            mock.call(bind=self.manager.engine)
        )
        self.assertTrue(self.manager.api.create.called)

    @mock.patch('os.path.exists', return_value=True)
    def test_create_db_version_control(self, mock_os_exists):
        """
        Tests that :meth:`database.versioning.DatabaseManager.create_db`
        calls the version control method of the API if the migrate repository
        exists, and a new database is created.

        :param mock.MagicMock mock_os_exists: A mock call to
            :meth:`os.path.exists`. Its return value of true tests the code
            as if a migrate repo exists
        """
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
    """
    Contains unit tests for
    :meth:`database.versioning.DatabaseManager.create_migration_script`
    """
    def setUp(self):
        TestDatabaseManager.setUp(self)
        self.manager.api.db_version = mock.MagicMock(new=1)

    @mock.patch('%s.eval' % builtin_string)
    @mock.patch('%s.open' % builtin_string)
    @mock.patch('omicron_server.database.versioning.types.ModuleType',
                return_value=MockModule())
    def test_migrate_db(self, mock_module, mock_open, mock_exec):
        """
        Tests the method

        :param mock.MagicMock mock_module: A mock call to the ``eval``
            function, used to evaluate and run the migration script.
        :param mock.MagicMock mock_open: A mock call to the function that
            opens the file to be evaluated
        :param mock.MagicMock mock_exec: A mock call to the temporary
            module that holds our migration script prior to writing
        """
        self.manager.create_migration_script()

        self.assertTrue(mock_exec.called)
        self.assertTrue(mock_open.called)
        self.assertTrue(mock_module.called)


class TestUpgradeDB(TestDatabaseManager):
    """
    Contains tests for :meth:`database.versioning.DatabaseManager.upgrade_db`
    """
    def setUp(self):
        TestDatabaseManager.setUp(self)
        self.manager.api.db_version = \
            mock.MagicMock(return_value=1)

        self.mock_upgrade_call = mock.call(
            self.manager.database_url, self.manager.migrate_repo
        )

    def test_upgrade_db(self):
        """
        Tests the method
        """
        self.manager.upgrade_db()

        self.assertEqual(
            self.manager.api.upgrade.call_args, self.mock_upgrade_call
        )


class TestDowngradeDB(TestDatabaseManager):
    """
    Contains tests for :meth:`database.versioning.DatabaseManager.downgrade_db`
    """
    def setUp(self):
        TestDatabaseManager.setUp(self)

        self.manager.api.db_version = mock.MagicMock(return_value=1)

        self.mock_downgrade_call = mock.call(
            self.manager.database_url, self.manager.migrate_repo,
            (self.manager.version - 1)
        )

    def test_downgrade_db(self):
        """
        Tests the method
        """
        self.manager.downgrade_db()

        self.assertEqual(
            self.manager.api.downgrade.call_args, self.mock_downgrade_call
        )


class TestRepr(TestDatabaseManager):
    """
    Tests :meth:`database.versioning.DatabaseManager.__repr__`
    """
    def test_repr(self):
        """
        Runs the test
        """
        self.assertEqual(
            self.manager.__repr__(),
            '%s(engine=%s, url=%s, migrate_repo=%s, api=%s)' % (
                self.manager.__class__.__name__, self.manager.engine,
                self.manager.database_url,
                self.manager.migrate_repo, self.manager.api
            )
        )
