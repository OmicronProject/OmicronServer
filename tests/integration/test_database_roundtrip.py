"""
Tests that the server can successfully write and read from the database
in a "Round Trip"
"""
from omicron_server.database.sessions import ContextManagedSession
from omicron_server.config import default_config as conf
from omicron_server.database.models.users import User
from tests.integration import TestCaseWithDatabase

__author__ = 'Michal Kononenko'


class TestDatabaseRoundTrip(TestCaseWithDatabase):
    """
    Tests that SQLAlchemy is successfully able to connect to the database,
    store an object in the DB, and retrieve it successfully.
    """
    def setUp(self):
        TestCaseWithDatabase.setUp(self)
        self.username = 'scott'
        self.password = 'tiger'
        self.email = 'scott@tiger.com'
        self.object_to_write = User(self.username, self.password, self.email)

        self.session = ContextManagedSession(bind=conf.DATABASE_ENGINE)

    def test_write(self):
        """
        Tests the round trip
        """
        with self.session() as session:
            session.add(self.object_to_write)

        with self.session() as session:
            user = session.query(self.object_to_write.__class__).filter_by(
                username=self.username
            ).first()

        self.assertIsInstance(user, self.object_to_write.__class__)
