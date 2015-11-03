"""
Contains unit tests for :mod:`views`
"""
import unittest
from api_server import app
from db_models import metadata, ContextManagedSession
import logging
import json
import api_views as views
from sqlalchemy import create_engine

__author__ = 'Michal Kononenko'

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

test_engine = create_engine('sqlite:///')
views.database_session = ContextManagedSession(bind=test_engine)


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
        cls.headers = {'content-type': 'application/json'}
        metadata.create_all(bind=test_engine)

    @classmethod
    def tearDownClass(cls):
        metadata.drop_all(bind=test_engine)


class TestRenderWelcomePage(TestView):
    def setUp(self):
        self.request_method = self.client.get

    def test_page(self):
        self.assertEqual(self.request_method('/').status_code, 200)


class TestCreateUser(TestView):
    def setUp(self):
        self.request_method = self.client.post
        self.url = 'api/v1/users'

    def test_post(self):
        data_to_post = {
            'username': 'scott',
            'password': 'tiger',
            'email': 'scott@tiger.com'
        }

        r = self.request_method(self.url, data=json.dumps(data_to_post),
                                headers=self.headers)
        self.assertEqual(r.status_code, 201)

    def test_post_bad_data(self):
        data_to_post = {
            'user': 'scott',
            'password': 'tiger',
            'email': 'scott@tiger.com'
        }
        r = self.request_method(self.url, data=json.dumps(data_to_post),
                                headers=self.headers)
        self.assertEqual(r.status_code, 400)