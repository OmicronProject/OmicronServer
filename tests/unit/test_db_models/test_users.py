import unittest
from freezegun import freeze_time
import mock
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import db_models.db_sessions
import db_models.users
from db_schema import metadata
from uuid import uuid1
from config import default_config as conf
from hashlib import sha256

__author__ = 'Michal Kononenko'


class TestToken(unittest.TestCase):
    engine = create_engine('sqlite://')
    time_to_freeze = datetime.utcnow()

    def setUp(self):
        self.token_string = str(uuid1())
        self.expiration_date = self.time_to_freeze + timedelta(seconds=1800)


class TestTokenConstructor(TestToken):

    def setUp(self):
        TestToken.setUp(self)
        self.guid_salt = uuid1()
        self.token_string = 'foobarbaz123456'

    @freeze_time(TestToken.time_to_freeze)
    @mock.patch('db_models.users.uuid1')
    @mock.patch('db_models.users.Token._hash_token')
    def test_constructor_with_expiration_date(
            self, mock_hash_token, mock_uuid1
    ):
        mock_uuid1.return_value = self.guid_salt

        token = db_models.users.Token(self.token_string, self.expiration_date)
        self.assertIsInstance(token, db_models.users.Token)

        self.assertEqual(token.salt, str(self.guid_salt))
        self.assertEqual(mock.call(), mock_uuid1.call_args)

        self.assertEqual(self.expiration_date, token.expiration_date)
        self.assertEqual(self.time_to_freeze, token.date_created)

        self.assertEqual(
            mock.call(self.token_string), mock_hash_token.call_args
        )

    @freeze_time(TestToken.time_to_freeze)
    @mock.patch('db_models.users.uuid1')
    @mock.patch('db_models.users.Token._hash_token')
    def test_constructor_no_expiration_date(self, mock_hash, mock_guid):
        mock_guid.return_value = self.guid_salt

        token = db_models.users.Token(self.token_string)
        expiration_date = self.time_to_freeze + timedelta(seconds=conf.DEFAULT_TOKEN_EXPIRATION_TIME)

        self.assertEqual(expiration_date, token.expiration_date)
        self.assertTrue(mock_hash.called)
        self.assertTrue(mock_guid.called)


class TestHashToken(TestToken):
    def setUp(self):
        TestToken.setUp(self)
        self.salt = str(uuid1())
        self.token = db_models.users.Token(self.token_string)
        self.token.salt = self.salt

    @mock.patch('db_models.users.sha256')
    def test_hash_token(self, mock_sha256):
        mock_sha256.return_value = sha256('foobarbaz123456'.encode('ascii'))
        self.token._hash_token(self.token_string)

        self.assertEqual(
            mock.call(self.salt.encode('ascii')),
            mock_sha256.call_args_list[0]
        )

        second_hash_call = mock.call(
            ("%s%s" % (mock_sha256.return_value.hexdigest(),
                        self.token_string)
             ).encode('ascii')
        )

        self.assertEqual(
            second_hash_call, mock_sha256.call_args_list[1]
        )


class TestVerifyToken(TestToken):
    def setUp(self):
        TestToken.setUp(self)
        self.token = db_models.users.Token(self.token_string)

    @freeze_time(TestToken.time_to_freeze)
    @mock.patch('db_models.users.Token._hash_token')
    def test_verify_token(self, mock_hash):
        mock_hash.return_value = self.token.token_hash

        self.token.expiration_date = self.time_to_freeze - timedelta(seconds=1)
        self.assertGreater(self.time_to_freeze, self.token.expiration_date)

        self.assertFalse(self.token.verify_token(self.token_string))

        self.assertFalse(mock_hash.called)

        self.token.expiration_date = self.time_to_freeze + timedelta(seconds=1)
        self.assertLess(self.time_to_freeze, self.token.expiration_date)

        self.assertTrue(self.token.verify_token(self.token_string))

        self.assertTrue(mock_hash.called)

    @freeze_time(TestToken.time_to_freeze)
    def test_revoke_token(self):
        self.token.revoke()
        self.assertEqual(self.token.expiration_date, self.time_to_freeze)



class TestUser(unittest.TestCase):
    engine = create_engine('sqlite://')

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