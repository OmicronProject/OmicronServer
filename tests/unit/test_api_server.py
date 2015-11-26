"""
Contains unit tests for :mod:`api_server`
"""
import unittest
import mock
from db_models import User, metadata, ContextManagedSession
import api_server
import json
from sqlalchemy import create_engine

__author__ = 'Michal Kononenko'

test_engine = create_engine('sqlite:///')
api_server.sessionmaker = mock.MagicMock(
    return_value=ContextManagedSession(bind=test_engine)
)


class TestHelloWorld(unittest.TestCase):
    def setUp(self):
        self.app = api_server.app
        self.client = self.app.test_client()
        self.request_method = self.client.get
        self.url = '/'

        self.headers = {'content-type': 'application/json'}

    def test_hello_world(self):
        r = self.request_method(self.url, headers=self.headers)
        self.assertEqual(r.status_code, 200)


class TestAPIServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = api_server.app
        cls.username = 'scott'
        cls.password = 'tiger'
        cls.email = 'scott@tiger.com'

        cls.user = User(cls.username, cls.password, cls.email)

        api_server.g = mock.MagicMock()

        api_server.g.user = cls.user

        cls.client = cls.app.test_client()
        cls.headers = {'content-type': 'application/json'}

        api_server.auth.verify_password_callback = mock.MagicMock(
            return_value=True
        )

        metadata.create_all(bind=test_engine)

    @classmethod
    def tearDownClass(cls):
        metadata.drop_all(bind=test_engine)


class TestGetAuthToken(TestAPIServer):
    def setUp(self):
        self.url = 'api/v1/token'
        self.token = 'mock_token'
        self.request_method = self.client.post
        self.user.generate_auth_token = mock.MagicMock(
            return_value=self.token.encode('ascii')
        )

    def test_create_auth_token(self):
        response = self.request_method(self.url, headers=self.headers)
        self.assertEqual(response.status_code, 201)

        json_dict = json.loads(response.data.decode('utf-8'))

        self.assertEqual(self.token, json_dict['token'])


