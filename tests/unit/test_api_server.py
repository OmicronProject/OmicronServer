"""
Contains unit tests for :mod:`api_server`
"""
__author__ = 'Michal Kononenko'

import unittest
import mock
from db_models import User
import api_server
import json

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