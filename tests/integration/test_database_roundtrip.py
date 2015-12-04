"""
Tests that the server can successfully write and read from the database
in a "Round Trip"
"""
from tests.integration import TestWithDatabase
from db_models.db_sessions import ContextManagedSession
from db_models.users import User
from config import default_config as conf

__author__ = 'Michal Kononenko'


class TestDatabaseRoundTrip(TestWithDatabase):

    def setUp(self):
        self.username = 'scott'
        self.password = 'tiger'
        self.email = 'scott@tiger.com'
        self.object_to_write = User(self.username, self.password, self.email)

        self.session = ContextManagedSession(bind=conf.DATABASE_ENGINE)

    def test_write(self):

        with self.session() as session:
            session.add(self.object_to_write)

        with self.session() as session:
            user = session.query(self.object_to_write.__class__).filter_by(
                username=self.username
            ).first()

        self.assertIsInstance(user, self.object_to_write.__class__)
