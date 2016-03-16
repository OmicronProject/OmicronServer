"""
Contains unit tests for :mod:`api_server`
"""
from tests import TestCaseWithAppContext
import json
from datetime import datetime
import mock
from omicron_server.database.models.users import User, Administrator
from omicron_server.database import Token
from omicron_server.database.sessions import ContextManagedSession
from freezegun import freeze_time
from sqlalchemy import create_engine
from omicron_server import api_server
from omicron_server.database.schema import metadata
import uuid
from flask import jsonify

__author__ = 'Michal Kononenko'

test_engine = create_engine('sqlite:///')


class TestGetRequestGuid(TestCaseWithAppContext):
    def setUp(self):
        TestCaseWithAppContext.setUp(self)
        self.request_id = uuid.uuid1()

    @mock.patch('omicron_server.api_server.uuid1')
    def test_get_id(self, mock_guid_maker):
        mock_guid_maker.return_value = self.request_id
        api_server.setup_request()
        self.assertEqual(
            api_server.g.request_id,
            str(self.request_id)
        )


class TestAddRequestGuidToHeader(TestCaseWithAppContext):
    def setUp(self):
        TestCaseWithAppContext.setUp(self)
        self.response = jsonify({'message': 'test'})
        self.request_id = str(uuid.uuid1())

        api_server.g.request_id = self.request_id
        api_server.g.session = mock.MagicMock()

    def tearDown(self):
        del api_server.g.request_id
        TestCaseWithAppContext.tearDown(self)

    def test_add(self):
        response = api_server.teardown_request(self.response)
        self.assertEqual(
            response.headers['Request-Id'],
            self.request_id
        )

        self.assertTrue(api_server.g.session.close.called)


class TestHelloWorld(TestCaseWithAppContext):
    """
    Tests :meth:`api_server.hello_world`
    """
    def setUp(self):
        TestCaseWithAppContext.setUp(self)
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


class TestAPIServer(TestCaseWithAppContext):
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
        TestAPIServer.setUp(self)
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

        self.assertTrue(
                self.user.generate_auth_token.called
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
        TestAPIServer.setUp(self)
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


class TestHandleTokenLogout(TestAPIServer):
    """
    Contains unit tests for
    :meth:`omicron_server.api_server._handle_token_logout`s
    """
    def setUp(self):
        TestAPIServer.setUp(self)
        self.user_to_logout = User('foo', 'bar', 'foo@bar.com')
        self.request = mock.MagicMock()

        self.token_string = str(uuid.uuid4())

        self.auth_token = Token(self.token_string, owner=self.user_to_logout)
        self.auth_token.revoke = mock.MagicMock()

    def test_request_json(self):
        request = mock.MagicMock()
        request.json = None

        response = api_server._handle_token_logout(
                request, self.user_to_logout
        )

        self.assertEqual(response.status_code, 400)

    def test_body_has_no_token(self):
        self.request.json = {
            'no_token_key': "no token"
        }

        with self.assertRaises(KeyError):
            self.request.json['token']

        response = api_server._handle_token_logout(
            self.request, self.user_to_logout
        )

        self.assertEqual(response.status_code, 400)

    @mock.patch('omicron_server.api_server.Token.from_database_session',
                return_value=None)
    def test_unable_to_get_token(self, mock_token_constructor):
        self.request.json = {
            'token': self.token_string
        }

        response = api_server._handle_token_logout(
            self.request, self.user_to_logout
        )

        self.assertEqual(response.status_code, 400)
        self.assertTrue(mock_token_constructor.called)

    @mock.patch('omicron_server.api_server.Token.from_database_session')
    def test_token_revoke(self, mock_token_constructor):
        mock_token_constructor.return_value=self.auth_token

        self.request.json = {'token': self.token_string}

        response = api_server._handle_token_logout(
            self.request, self.user_to_logout
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.auth_token.revoke.called)

    @mock.patch('omicron_server.api_server.Token.from_database_session')
    def test_unauthorized_revoke(self, mock_token_constructor):
        auth_token = Token(
            self.token_string, owner=User('bad_name', 'bad_pass', 'bad_email')
        )

        self.assertNotEqual(auth_token.owner, self.user_to_logout)
        self.assertFalse(isinstance(self.user_to_logout, Administrator))

        mock_token_constructor.return_value = auth_token
        self.request.json = {'token': self.token_string}

        response = api_server._handle_token_logout(
            self.request, self.user_to_logout
        )

        self.assertEqual(response.status_code, 403)
