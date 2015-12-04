import unittest

import mock
from sqlalchemy import create_engine

import db_models.db_sessions
import db_models.users
from db_schema import metadata

__author__ = 'Michal Kononenko'


class TestUser(unittest.TestCase):
    engine = create_engine('sqlite:///')

    @classmethod
    def setUpClass(cls):
        metadata.create_all(bind=cls.engine)

    def setUp(self):
        self.username = 'scott'
        self.password = 'tiger'
        self.email = 'scott@tiger.com'
        self.base_session = \
            db_models.db_sessions.ContextManagedSession(
                bind=self.engine
            )

    @classmethod
    def tearDownClass(cls):
        metadata.drop_all(bind=cls.engine)


class TestUserConstructor(TestUser):

    @mock.patch('db_models.users.User.hash_password')
    def test_constructor(self, mock_hash_function):

        mock_hash_function.return_value = 'hashed_password'

        user = db_models.users.User(self.username, self.password, self.email)
        self.assertIsInstance(user, db_models.users.User)
        self.assertEqual(user.username, self.username)
        self.assertEqual(user.email_address, self.email)
        self.assertEqual(user.password_hash, mock_hash_function.return_value)

        mock_hash_function_call = mock.call(self.password)
        self.assertEqual(mock_hash_function.call_args, mock_hash_function_call)


class TestHashPassword(TestUser):
    def setUp(self):
        TestUser.setUp(self)
        self.user = db_models.users.User(self.username, self.password, self.email)

    @mock.patch('db_models.users.pwd_context.encrypt')
    def test_hash_password(self, mock_encrypt):
        self.assertEqual(
            mock_encrypt.return_value, db_models.users.User.hash_password(self.password)
        )

        mock_encrypt_call = mock.call(self.password)
        self.assertEqual(
            mock_encrypt_call, mock_encrypt.call_args
        )


class TestVerifyPassword(TestUser):
    def setUp(self):
        TestUser.setUp(self)
        self.user = db_models.users.User(self.username, self.password, self.email)
        self.bad_password = 'invalid'

        self.assertNotEqual(self.password, self.bad_password)

    def test_verify_good_password(self):
        self.assertTrue(self.user.verify_password(self.password))

    def test_verify_bad_password(self):
        self.assertFalse(self.user.verify_password(self.bad_password))


class TestGenerateAuthToken(TestUser):
    def setUp(self):
        TestUser.setUp(self)
        self.user = db_models.users.User(self.username, self.password, self.email)
        self.mock_token = 'foobarbaz123456'

    @mock.patch('db_models.users.Serializer.dumps')
    def test_generate_auth_token(self, mock_serializer):
        mock_serializer.return_value = self.mock_token
        mock_dumps_call = mock.call({'id': self.user.id})

        self.assertEqual(self.mock_token, self.user.generate_auth_token())
        self.assertEqual(mock_dumps_call, mock_serializer.call_args)


class TestVerifyAuthToken(TestUser):
    def setUp(self):
        TestUser.setUp(self)
        self.user = db_models.users.User(self.username, self.password, self.email)
        self.mock_token ='foobarbaz123456'

        with self.base_session() as session:
            session.add(self.user)

    def tearDown(self):
        with self.base_session() as session:
            user = session.query(db_models.users.User).\
                filter_by(id=1).first()
            session.delete(user)

    @mock.patch('db_models.users.Serializer.loads')
    def test_verify_token(self, mock_serializer):
        mock_serializer.return_value = {'id': 1}
        returned_data = db_models.users.User.verify_auth_token(self.mock_token)

        self.assertEqual(1, returned_data)

    @mock.patch('db_models.users.Serializer.loads')
    def test_verify_token_signature_expired(self, mock_serializer):
        mock_serializer.side_effect = \
            db_models.users.SignatureExpired('test_error')

        self.assertIsNone(
            db_models.users.User.verify_auth_token(self.mock_token))

    @mock.patch('db_models.users.Serializer.loads')
    def test_verify_token_bad_signature(self, mock_serializer):
        mock_serializer.side_effect = \
            db_models.users.BadSignature('test_error')
        self.assertIsNone(
            db_models.users.User.verify_auth_token(self.mock_token))


class TestGet(TestUser):
    def setUp(self):
        TestUser.setUp(self)
        self.user = db_models.users.User(self.username, self.password, self.email)
        self.expected_result = {
            'username': self.username,
            'email': self.email,
            'date_created': self.user.date_created.isoformat()
        }

    def test_get(self):
        self.assertEqual(self.expected_result, self.user.get)


class TestGetFull(TestUser):
    def setUp(self):
        TestUser.setUp(self)
        self.user = db_models.users.User(self.username, self.password, self.email)
        self.expected_result = {
            'username': self.username,
            'email': self.email,
            'date_created': self.user.date_created.isoformat()
        }

    def test_get_full(self):
        self.assertEqual(self.expected_result, self.user.get_full)


class TestUserRepr(TestUser):
    def setUp(self):
        TestUser.setUp(self)
        self.user = db_models.users.User(self.username, self.password, self.email)
        self.expected_result = '%s(%s, %s, %s)' % (
            self.user.__class__.__name__, self.username,
            self.user.password_hash, self.email
        )

    def test_repr(self):
        self.assertEqual(self.expected_result, self.user.__repr__())