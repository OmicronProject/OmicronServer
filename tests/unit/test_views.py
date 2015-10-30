"""
Contains unit tests for :mod:`views`
"""
__author__ = 'Michal Kononenko'

import unittest
from api_server import app
import config
from db_models import metadata
from sqlalchemy import create_engine

db_engine = create_engine('sqlite://')


class TestView(unittest.TestCase):
    """
    Contains generic set-up for each view
    """
    @classmethod
    def setUpClass(cls):
        """
        Set up the test client
        :return:
        """
        cls.client = app.test_client(use_cookies=True)
        metadata.create_all(bind=db_engine)


class TestRenderWelcomePage(TestView):
    def setUp(self):
        self.request_method = self.client.get

    def test_page(self):
        self.assertEqual(self.request_method('/').status_code, 200)