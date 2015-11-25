"""
Contains unit tests for :mod:`auth`
"""
import unittest
import auth
import mock
from db_models import User, metadata
from sqlalchemy import create_engine

__author__ = 'Michal Kononenko'


class TestAuth(unittest.TestCase):
    engine = create_engine('sqlite:///')

    auth.conf.DATABASE_ENGINE = engine

    @classmethod
    def setUpClass(cls):
        cls.username = 'scott'
        cls.password = 'tiger'
        cls.email = 'scott@tiger.com'
        metadata.create_all(bind=cls.engine)

    @classmethod
    def tearDownClass(cls):
        metadata.drop_all(bind=cls.engine)


class TestVerifyPassword(TestAuth):

    def setUp(self):

        self.user = User(self.username, self.password, self.email)

        auth.g = mock.MagicMock()

        with auth.sessionmaker(self.engine) as session:
            session.add(self.user)

        self.user = self.user.__class__(
            self.username, self.password, self.email
        )

    def tearDown(self):
        with auth.sessionmaker(self.engine) as session:
            user = session.query(self.user.__class__).filter_by(
                username=self.username
            ).first()
            if user is not None:
                session.delete(user)

    def test_auth_token_correct(self):

        with mock.patch(
                'api_server.User.verify_auth_token', return_value=self.user
        ) as mock_verify_auth:

            self.assertTrue(auth.verify_password(
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

        self.assertTrue(auth.verify_password(
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
        with auth.sessionmaker(self.engine) as session:
            user = session.query(self.user.__class__).filter_by(
                username=self.username
            ).first()
            session.delete(user)

        self.assertFalse(auth.verify_password(
            self.username, self.password))

        self.assertFalse(mock_verify.called)

    @mock.patch('api_server.User.verify_password', return_value=False)
    def test_user_query_bad_password(self, mock_verify):
        self.assertFalse(auth.verify_password(
            self.username, self.password
        ))

        self.assertTrue(mock_verify.called)

    @mock.patch('api_server.User.verify_auth_token')
    def test_user_query_token_adds_to_g(self, mock_verify_auth_token):

        mock_verify_auth_token.return_value = self.user

        self.assertTrue(auth.verify_password(
            self.username, self.password
        ))

        self.assertEqual(auth.g.user, self.user)

        self.assertEqual(mock_verify_auth_token.call_args,
                         mock.call(self.username))

    @mock.patch('api_server.User.verify_auth_token', return_value=False)
    @mock.patch('sqlalchemy.orm.query.Query.first')
    @mock.patch('api_server.User.verify_password', return_value=True)
    def test_user_password_verify_adds_to_g(
            self, mock_verify_password, mock_query, mock_verify_token
    ):
        mock_query.return_value = self.user

        self.assertTrue(auth.verify_password(
            self.username, self.password
        ))

        self.assertEqual(auth.g.user, self.user)

        self.assertEqual(mock_query.call_args, mock.call())
        self.assertEqual(mock_verify_password.call_args,
                         mock.call(self.password))
        self.assertEqual(mock_verify_token.call_args,
                         mock.call(self.username))
