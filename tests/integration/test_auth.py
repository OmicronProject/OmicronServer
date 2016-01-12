"""
Contains integration tests for :mod:`auth`, performing authentication
without stubbing out any functionality.
"""
import unittest
from config import default_config as conf
from database import User, ContextManagedSession
from database.schema import metadata
import auth
from api_server import app
from base64 import b64encode
import json
from uuid import uuid4

__author__ = 'Michal Kononenko'
database_session = ContextManagedSession(bind=conf.DATABASE_ENGINE)


class TestAuth(unittest.TestCase):
    """
    Base class for testing :mod:`auth`
    """
    @classmethod
    def setUpClass(cls):
        """
        Set up the test database, and put the server into a request context
        requiring authentication.
        """
        cls.context = app.test_request_context(
            'api/v1/users'
        )
        cls.username = 'root'
        cls.password = 'toor'
        cls.email = 'scott@tiger.com'

        metadata.create_all(bind=conf.DATABASE_ENGINE)

        with database_session() as session:
            session.add(User(cls.username, cls.password, cls.email))

    @classmethod
    def tearDownClass(cls):
        """
        Clean up a test suite by dropping all tables in the test database.
        """
        metadata.drop_all(bind=conf.DATABASE_ENGINE)


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
