"""
Contains integration tests for :mod:`auth`, performing authentication
without stubbing out any functionality.
"""
import json
from base64 import b64encode
from uuid import uuid4
import omicron_server.auth as auth
from omicron_server.database import ContextManagedSession
from omicron_server.models import User
from omicron_server.config import default_config as conf
from tests.integration import TestCaseWithDatabase
from omicron_server import app
from copy import deepcopy

__author__ = 'Michal Kononenko'
database_session = ContextManagedSession(bind=conf.DATABASE_ENGINE)


class TestAuth(TestCaseWithDatabase):
    """
    Base class for testing :mod:`auth`
    """
    @classmethod
    def setUpClass(cls):
        """
        Set up the test database, and put the server into a request context
        requiring authentication.
        """
        TestCaseWithDatabase.setUpClass()
        cls.username = 'root'
        cls.password = 'toor'
        cls.email = 'scott@tiger.com'

    def setUp(self):
        TestCaseWithDatabase.setUp(self)
        self._clear_test_user(database_session)

        with database_session() as session:
            session.add(User(self.username, self.password, self.email))

    def tearDown(self):
        self._clear_test_user(database_session)
        TestCaseWithDatabase.tearDown(self)

    def _clear_test_user(self, db_session):
        with db_session() as session:
            users = session.query(User).filter_by(
                username=self.username
            ).all()
            for user in users:
                session.delete(user)


class TestVerifyPassword(TestAuth):
    """
    Tests the :meth:`auth.verify_password` callback
    """
    def test_verify_password_correct_credentials(self):
        """
        Tests that the callback returns ``True`` if the correct username and
        password are provided.
        """
        with self.context:
            self.assertTrue(auth.verify_password(self.username, self.password))

    def test_verify_incorrect_username_correct_pwd(self):
        """
        Tests that the callback returns ``False`` if an incorrect username
        but correct password are supplied.
        """
        bad_username = 'not a valid username'
        with self.context:
            self.assertFalse(auth.verify_password(bad_username, self.password))

    def test_verify_correct_uname_bad_pwd(self):
        """
        Tests that the callback returns ``False`` if the correct username but
        an incorrect password are supplied.
        """
        bad_password = 'notavalidpassword'
        with self.context:
            self.assertFalse(auth.verify_password(self.username, bad_password))


class TestVerifyToken(TestAuth):
    """
    Tests :meth:`auth._verify_token`
    """
    def setUp(self):
        """
        Starts up the server, and requests an authentication token using the
        correct login credentials.
        """
        TestAuth.setUp(self)
        self.client = app.test_client()
        self.headers = {
            'content-type': 'application/json',
            'Authorization': 'Basic %s' % b64encode(
                ('%s:%s' % (self.username, self.password)).encode('ascii')
            ).decode('ascii')
        }
        r = self.client.post('/tokens', headers=self.headers)

        self.assertEqual(r.status_code, 201)

        self.token = json.loads(r.data.decode('ascii'))['token']

    def test_token_auth(self):
        """
        Tests that the ``verify_password`` callback can authenticate a user
        when the correct token is provided.
        """
        with self.context:
            self.assertTrue(auth.verify_password(self.token))

    def test_token_auth_bad_token(self):
        """
        Tests that the user cannot be authenticated if an incorrect token is
        provided.
        """
        bad_token = str(uuid4())
        self.assertNotEqual(bad_token, self.token)

        with self.context:
            self.assertFalse(auth.verify_password(bad_token))
            self.assertTrue(auth.verify_password(self.token))


class TestAuthTokenVerification(TestAuth):
    def setUp(self):
        TestAuth.setUp(self)
        self.client = app.test_client()
        self.headers = {
            'content-type': 'application/json',
            'Authorization': 'Basic %s' % b64encode(
                ('%s:%s' % (self.username, self.password)).encode('ascii')
            ).decode('ascii')
        }

        r = self.client.post('/tokens', headers=self.headers)

        self.assertEqual(r.status_code, 201)

        self.token = json.loads(r.data.decode('ascii'))['token']

        self.token_auth_headers = deepcopy(self.headers)

        self.token_auth_headers['Authorization'] = 'Basic %s' % b64encode(
                ('%s:' % self.token).encode('ascii')
        ).decode('ascii')

        self.assertNotEqual(self.token_auth_headers, self.headers)

    def test_end_to_end_token_auth(self):

        request_with_username = self.client.get(
                '/users', headers=self.headers)
        self.assertEqual(request_with_username.status_code, 200)

        request_with_token = self.client.get(
                '/users', headers=self.token_auth_headers)
        self.assertEqual(request_with_token.status_code, 200)


class TestExpiredToken(TestAuth):
    def setUp(self):
        TestAuth.setUp(self)
        self.client = app.test_client()
        self.headers = {
            'content-type': 'application/json',
            'Authorization': self._encode_credentials(
                    self.username, self.password
            )
        }

        self.token_endpoint = '/tokens'
        self.authorized_endpoint = '/users'

        self.token = self._get_auth_token(self.token_endpoint, self.headers)

        self.token_headers = {
            'content-type': 'application/json',
            'Authorization': self._encode_credentials(self.token)
        }

    def test_token_revocation(self):
        """
        Tests the patch for bug #131. Checks that the user cannot sign in with
        an expired token.
        """
        response = self._make_authorized_request(
                self.authorized_endpoint, self.token_headers
        )
        self.assertEqual(response.status_code, 200)

        response = self._delete_token(self.token_endpoint, self.token_headers)
        self.assertEqual(response.status_code, 200)

        response = self._make_authorized_request(
                self.authorized_endpoint, self.token_headers
        )
        self.assertEqual(response.status_code, 401)

    @staticmethod
    def _encode_credentials(username_or_token='', password=''):
        auth_header = 'Basic %s' % b64encode(
                ('%s:%s' % (username_or_token, password)).encode('ascii')
        ).decode('ascii')

        return auth_header

    def _get_auth_token(self, token_url, headers):
        r = self.client.post(token_url, headers=headers)
        self.assertEqual(r.status_code, 201)

        token = json.loads(r.data.decode('ascii'))['token']
        return token

    def _make_authorized_request(self, url, headers):
        r = self.client.get(url, headers=headers)
        return r

    def _delete_token(self, url, headers):
        r = self.client.delete(url, headers=headers)
        return r
