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


class TestVerifyPassword(TestAPIServer):

    def setUp(self):

        self.user = User(self.username, self.password, self.email)

        api_server.g = mock.MagicMock()

        with api_server.sessionmaker() as session:
            session.add(self.user)

        self.user = self.user.__class__(
            self.username, self.password, self.email
        )

    def tearDown(self):
        with api_server.sessionmaker() as session:
            user = session.query(self.user.__class__).filter_by(
                username=self.username
            ).first()
            if user is not None:
                session.delete(user)

    def test_auth_token_correct(self):

        with mock.patch(
                'api_server.User.verify_auth_token', return_value=self.user
        ) as mock_verify_auth:

            self.assertTrue(api_server.verify_password(
                self.username, self.password
            )
            )
            self.assertEqual(
                mock_verify_auth.call_args,
                mock.call(self.username)
             )

    @mock.patch('api_server.User.verify_password', return_value=True)
    @mock.patch('api_server.User.verify_auth_token', return_value=False)
    def test_user_query(self, mock_check_auth_token, mock_verify_pwd):

        self.assertTrue(api_server.verify_password(
            self.username, self.password
        ))

        self.assertEqual(
            mock_verify_pwd.call_args,
            mock.call(self.password)
        )

        self.assertEqual(
            mock_check_auth_token.call_args,
            mock.call(self.username)
        )

    @mock.patch('api_server.User.verify_password', return_value=True)
    def test_user_query_no_user_found(self, mock_verify):
        with api_server.sessionmaker() as session:
            user = session.query(self.user.__class__).filter_by(
                username=self.username
            ).first()
            session.delete(user)

        self.assertFalse(api_server.verify_password(
            self.username, self.password))

        self.assertFalse(mock_verify.called)

    @mock.patch('api_server.User.verify_password', return_value=False)
    def test_user_query_bad_password(self, mock_verify):
        self.assertFalse(api_server.verify_password(
            self.username, self.password
        ))

        self.assertTrue(mock_verify.called)

    @mock.patch('api_server.User.verify_auth_token')
    def test_user_query_token_adds_to_g(self, mock_verify_auth_token):

        mock_verify_auth_token.return_value = self.user

        self.assertTrue(api_server.verify_password(
            self.username, self.password
        ))

        self.assertEqual(api_server.g.user, self.user)

        self.assertEqual(mock_verify_auth_token.call_args,
                         mock.call(self.username))

    @mock.patch('api_server.User.verify_auth_token', return_value=False)
    @mock.patch('sqlalchemy.orm.query.Query.first')
    @mock.patch('api_server.User.verify_password', return_value=True)
    def test_user_password_verify_adds_to_g(
            self, mock_verify_password, mock_query, mock_verify_token
    ):
        mock_query.return_value = self.user

        self.assertTrue(api_server.verify_password(
            self.username, self.password
        ))

        self.assertEqual(api_server.g.user, self.user)

        self.assertEqual(mock_query.call_args, mock.call())
        self.assertEqual(mock_verify_password.call_args,
                         mock.call(self.password))
        self.assertEqual(mock_verify_token.call_args,
                         mock.call(self.username))



