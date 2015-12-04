"""
Contains integration tests for the Omicron Server
"""
import unittest
import db_schema
from config import default_config as conf
from db_models import User, ContextManagedSession

__author__ = 'Michal Kononenko'


class TestWithDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db_schema.metadata.create_all(bind=conf.DATABASE_ENGINE)

    @classmethod
    def tearDownClass(cls):
        db_schema.metadata.drop_all(bind=conf.DATABASE_ENGINE)
