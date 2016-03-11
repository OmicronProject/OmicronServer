"""
Contains integration tests for the Omicron Server
"""
from tests import TestCaseWithAppContext
from omicron_server.config import default_config as conf
from omicron_server.database import schema

__author__ = 'Michal Kononenko'


class TestCaseWithDatabase(TestCaseWithAppContext):

    @classmethod
    def setUpClass(cls):
        schema.metadata.create_all(bind=conf.DATABASE_ENGINE)

    @classmethod
    def tearDownClass(cls):
        schema.metadata.drop_all(bind=conf.DATABASE_ENGINE)
