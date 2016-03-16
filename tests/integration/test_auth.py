"""
Contains integration tests for :mod:`auth`, performing authentication
without stubbing out any functionality.
"""
import json
from base64 import b64encode
from uuid import uuid4
import omicron_server.auth as auth
from omicron_server.database import User, ContextManagedSession
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
        with database_session() as session:
            users = session.query(User).filter_by(
                username=self.username
            ).all()
            for user in users:
                session.delete(user)

        with database_session() as session:
            session.add(User(self.username, self.password, self.email))

    def tearDown(self):
        TestCaseWithDatabase.tearDown(self)


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
        r = self.client.post('api/v1/token', headers=self.headers)

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

        r = self.client.post('api/v1/token', headers=self.headers)

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
