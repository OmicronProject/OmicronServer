"""
Contains unit tests for :mod:`api_server`
"""
import json
import unittest
from datetime import datetime

import mock
from omicron_server.database.models.users import User, Administrator
from omicron_server.database.sessions import ContextManagedSession
from freezegun import freeze_time
from sqlalchemy import create_engine

from omicron_server import api_server
from omicron_server.database.schema import metadata

__author__ = 'Michal Kononenko'

test_engine = create_engine('sqlite:///')


class TestHelloWorld(unittest.TestCase):
    """
    Tests :meth:`api_server.hello_world`
    """
    def setUp(self):
        api_server.database_session = ContextManagedSession(bind=test_engine)
        self.app = api_server.app
        self.client = self.app.test_client()
        self.request_method = self.client.get
        self.url = '/'

        self.headers = {'content-type': 'application/json'}

    def test_hello_world(self):
        """
        Tests that a request to the server's root endpoint returns 200,
        indicating that the server has set up and is running successfully.
        """
        r = self.request_method(self.url, headers=self.headers)
        self.assertEqual(r.status_code, 200)


class TestAPIServer(unittest.TestCase):
    """
    Base class for unit tests in :mod:`api_server`
    """

    @classmethod
    def setUpClass(cls):
        """
        Sets up basic parameters for testing in :mod:`api_server`.
        """
        api_server.database_session = ContextManagedSession(bind=test_engine)
        cls.app = api_server.app
        cls.username = 'scott'
        cls.password = 'tiger'
        cls.email = 'scott@tiger.com'

        cls.user = User(cls.username, cls.password, cls.email)

        api_server.g = mock.MagicMock()

        api_server.g.user = cls.user

        cls.client = cls.app.test_client()
        cls.headers = {'content-type': 'application/json'}

        metadata.create_all(bind=test_engine)

    @classmethod
    def tearDownClass(cls):
        """
        Tear down the tests
        """
        metadata.drop_all(bind=test_engine)


@mock.patch('omicron_server.api_server.auth.verify_password_callback',
            return_value=True)
@freeze_time('2016-01-01')
class TestGetAuthToken(TestAPIServer):
    """
    Tests :meth:`api_server.create_token`
    """
    def setUp(self):
        """
        Set up the tests by creating a mock token, and
        assigning it as a return value to ``self.user``, which
        is assigned to ``g.user``.
        """
        self.url = 'api/v1/token'
        self.token = 'mock_token'
        self.token_expiry_date = datetime.utcnow()
        self.request_method = self.client.post
        self.user.generate_auth_token = mock.MagicMock(
            return_value=(self.token, self.token_expiry_date)
        )
        api_server.g.authenticated_from_token = False

    def test_create_auth_token(self, mock_verify):
        response = self.request_method(self.url, headers=self.headers)
        self.assertEqual(response.status_code, 201)

        json_dict = json.loads(response.data.decode('utf-8'))

        self.assertEqual(self.token, json_dict['token'])
        self.assertEqual(
                self.token_expiry_date.isoformat(),
                json_dict['expiration_date']
         )

        self.assertTrue(mock_verify.called)

    def test_create_auth_token_with_expiration(self, mock_verify):
        seconds_to_exp = 1200
        url = '%s?expiration=%d' % (self.url, seconds_to_exp)

        response = self.request_method(url, headers=self.headers)
        self.assertEqual(response.status_code, 201)

        json_dict = json.loads(response.data.decode('utf-8'))
        self.assertEqual(self.token, json_dict['token'])

        self.assertEqual(
                mock.call(expiration=seconds_to_exp),
                self.user.generate_auth_token.call_args
        )

        self.assertTrue(mock_verify.called)

    def test_auth_token_prevent_token_renewal(self, mock_verify):
        """
        Tests that if a user requests a new token using an existing token, the
        request returns a ``401 UNAUTHORIZED`` status code. In order to
        request a token, the API consumer must sign in with their username and
        password
        """
        api_server.g.authenticated_from_token = True
        r = self.request_method(self.url, headers=self.headers)
        self.assertEqual(r.status_code, 401)
        self.assertTrue(mock_verify.called)


@mock.patch('omicron_server.api_server.auth.verify_password_callback',
            return_value=True)
class TestRevokeToken(TestAPIServer):
    """
    Tests :meth:`api_server.revoke_token`
    """
    token = mock.MagicMock()

    def setUp(self):
        self.url = 'api/v1/token'
        self.request_method = self.client.delete
        self.admin = Administrator(self.username, self.password, self.email)

    @mock.patch('sqlalchemy.orm.Query.first')
    @mock.patch('omicron_server.api_server.auth.login_required',
                new=lambda t: t)
    @mock.patch('omicron_server.database.User.current_token')
    def test_revoke_token(self, mock_cur_token, mock_query, mock_auth):
        mock_query.return_value = self.user
        response = self.request_method(self.url, headers=self.headers)
        self.assertEqual(response.status_code, 200)

        self.assertTrue(mock_cur_token.first().revoke.called)
        self.assertTrue(mock_auth.called)

    @mock.patch('sqlalchemy.orm.Query.first')
    @mock.patch('omicron_server.api_server.auth.login_required',
                new=lambda t: t)
    @mock.patch('omicron_server.api_server.g')
    @mock.patch('omicron_server.database.User.current_token')
    def test_administrator_revoke(self, mock_cur_token, mock_g, mock_query,
                                  mock_auth):
        mock_g.user = self.admin
        mock_query.return_value = self.admin

        response = self.request_method(self.url, headers=self.headers)

        self.assertEqual(response.status_code, 200)

        self.assertTrue(mock_cur_token.first().revoke.called)
        self.assertTrue(mock_auth.called)

    @mock.patch('sqlalchemy.orm.Query.first', return_value=None)
    @mock.patch('omicron_server.api_server.auth.login_required',
                new=lambda t: t)
    @mock.patch('omicron_server.api_server.g')
    @mock.patch('omicron_server.database.User.current_token')
    def test_administrator_revoke_user_not_found(self, mock_cur_token, mock_g,
                                                 mock_query, mock_auth):
        url = '%s?username=%s' % (self.url, self.username)
        mock_g.user = self.admin

        response = self.request_method(url, headers=self.headers)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(mock_cur_token.first().revoke.called)
        self.assertTrue(mock_auth.called)

    @mock.patch('omicron_server.api_server.g')
    @mock.patch('omicron_server.api_server._handle_token_logout')
    def test_administrator_revoke_token(self, mock_handler, mock_g, mock_auth):
        mock_g.authenticated_from_token = False

        mock_g.user = self.admin

        self.request_method(self.url, headers=self.headers)

        self.assertTrue(mock_handler.called)
        self.assertTrue(mock_auth.called)
