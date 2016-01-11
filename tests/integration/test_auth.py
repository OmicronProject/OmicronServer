import unittest
from config import default_config as conf
from database import User, ContextManagedSession
from database.schema import metadata
import auth
from api_server import app
from base64 import b64encode
import json

__author__ = 'Michal Kononenko'
database_session = ContextManagedSession(bind=conf.DATABASE_ENGINE)


class TestAuth(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
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
        metadata.drop_all(bind=conf.DATABASE_ENGINE)


class TestVerifyPassword(TestAuth):

    def test_verify_password_correct_credentials(self):
        with self.context:
            self.assertTrue(auth.verify_password(self.username, self.password))

    def test_verify_incorrect_username_correct_pwd(self):
        bad_username = 'not a valid username'
        with self.context:
            self.assertFalse(auth.verify_password(bad_username, self.password))

    def test_verify_correct_uname_bad_pwd(self):
        bad_password = 'notavalidpassword'
        with self.context:
            self.assertFalse(auth.verify_password(self.username, bad_password))


class TestVerifyToken(TestAuth):
    def setUp(self):
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
        with self.context:
            self.assertTrue(auth.verify_password(self.token))
