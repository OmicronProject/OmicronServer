"""
Contains unit tests for :mod:`auth`
"""
import unittest
import auth
import mock
from db_schema import metadata
from db_models.users import User, Token
from sqlalchemy import create_engine
from db_models.db_sessions import ContextManagedSession
from uuid import uuid1

__author__ = 'Michal Kononenko'


class TestAuth(unittest.TestCase):
    engine = create_engine('sqlite:///')
    auth.database_session = ContextManagedSession(bind=engine)

    @classmethod
    def setUpClass(cls):
        cls.username = 'scott'
        cls.password = 'tiger'
        cls.email = 'scott@tiger.com'
        metadata.create_all(bind=cls.engine)

    @classmethod
    def tearDownClass(cls):
        metadata.drop_all(bind=cls.engine)


class TestVerifyUser(TestAuth):

    def setUp(self):

        self.user = User(self.username, self.password, self.email)

        auth.g = mock.MagicMock()

        with auth.database_session() as session:
            session.add(self.user)

        self.user = self.user.__class__(
            self.username, self.password, self.email
        )

    def tearDown(self):
        with auth.database_session() as session:
            user = session.query(self.user.__class__).filter_by(
                username=self.username
            ).first()
            if user is not None:
                session.delete(user)

    def test_auth_token_correct(self):

        with mock.patch(
                'sqlalchemy.orm.Query.first', return_value=self.user
        ) as mock_verify_auth:

            self.assertTrue(auth.verify_password(
                self.username, self.password
            )
            )
            self.assertEqual(
                mock_verify_auth.call_args,
                mock.call()
             )

    @mock.patch('auth.User.verify_password', return_value=True)
    def test_user_query(self, mock_verify_pwd):

        self.assertTrue(auth.verify_password(
            self.username, self.password
        ))

        self.assertEqual(
            mock_verify_pwd.call_args,
            mock.call(self.password)
        )

    @mock.patch('auth.User.verify_password', return_value=True)
    def test_user_query_no_user_found(self, mock_verify):
        with auth.database_session() as session:
            user = session.query(self.user.__class__).filter_by(
                username=self.username
            ).first()
            session.delete(user)

        self.assertFalse(auth.verify_password(
            self.username, self.password))

        self.assertFalse(mock_verify.called)

    @mock.patch('auth.User.verify_password', return_value=False)
    def test_user_query_bad_password(self, mock_verify):
        self.assertFalse(auth.verify_password(
            self.username, self.password
        ))

        self.assertTrue(mock_verify.called)

    def test_user_query_token_adds_to_g(self):

        self.assertTrue(auth.verify_password(
            self.username, self.password
        ))

        self.assertIsInstance(auth.g.user, self.user.__class__)

    @mock.patch('auth.User.verify_auth_token', return_value=False)
    @mock.patch('sqlalchemy.orm.query.Query.first')
    @mock.patch('auth.User.verify_password', return_value=True)
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


class TestVerifyPassword(TestAuth):
    def setUp(self):
        TestAuth.setUp(self)
        self.user = User(self.username, self.password, self.email)
        self.token_string = str(uuid1())

        self.token = Token(self.token_string, owner=self.user)

        with auth.database_session() as session:
            session.add(self.user)
            session.add(self.token)

        auth.g = mock.MagicMock()

    def tearDown(self):
        with auth.database_session() as session:
            user = session.query(self.user.__class__).filter_by(
                username=self.username
            ).first()

            token = session.query(self.token.__class__).filter_by(
                user_id=user.id
            ).first()

            if user is not None:
                session.delete(user)

            if token is not None:
                session.delete(token)

    def test_verify_token(self):
        self.assertTrue(auth.verify_password(self.token_string))
        self.assertEqual(auth.g.user, self.user)

    @mock.patch('sqlalchemy.orm.Query.first', return_value=None)
    def test_verify_token_no_token_found(self, mock_first):
        self.assertFalse(auth.verify_password(self.token_string))
        self.assertTrue(mock_first.called)

    @mock.patch('db_models.users.Token.verify_token', return_value=False)
    def test_verify_token_bad_token(self, mock_check_token):
        self.assertFalse(auth.verify_password(self.token_string))
        self.assertTrue(mock_check_token.called)
