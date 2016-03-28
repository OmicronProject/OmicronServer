"""
Contains tests for the API
"""
import unittest
from omicron_server import app
from sqlalchemy import create_engine
from omicron_server.config import default_config as conf
from copy import deepcopy
from omicron_server.database.schema import metadata

__author__ = 'Michal Kononenko'

original_engine = create_engine(conf.DATABASE_URL)
original_url = deepcopy(conf.DATABASE_URL)


class TestCaseWithAppContext(unittest.TestCase):
    def setUp(self):
        self.context = app.test_request_context()
        self.context.push()

    def tearDown(self):
        self.context.pop()


class TestCaseWithDatabase(TestCaseWithAppContext):
    def setUp(self):
        TestCaseWithAppContext.setUp(self)
        self.database_url = 'sqlite://'
        self.database_engine = create_engine(self.database_url)

        conf.DATABASE_URL = self.database_url
        conf.DATABASE_ENGINE = self.database_engine

        metadata.create_all(bind=conf.DATABASE_ENGINE)

    def tearDown(self):
        conf.DATABASE_URL = original_url
        conf.DATABASE_ENGINE = original_engine

        metadata.drop_all(bind=conf.DATABASE_ENGINE)

        TestCaseWithAppContext.tearDown(self)
