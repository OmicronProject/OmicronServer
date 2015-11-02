"""
Contains unit tests for :mod:`db_models`
"""
import unittest
import unittest.mock as mock
import db_models as models
from sqlalchemy import create_engine
from db_schema import metadata

__author__ = 'Michal Kononenko'


class TestSessionMaker(unittest.TestCase):

    @mock.patch('db_models.sqlalchemy_sessionmaker')
    def test_sessionmaker_no_args(self, mock_sessionmaker):
        mock_session = mock.MagicMock()
        mock_sessionmaker.return_value = mock_session

        mock_sessionmaker_call = mock.call(bind=models.sqlalchemy_engine)

        self.assertEqual(mock_session, models.sessionmaker())
        self.assertEqual(mock_sessionmaker.call_args, mock_sessionmaker_call)

    @mock.patch('db_models.sqlalchemy_sessionmaker')
    def test_sessionmaker_with_engine(self, mock_sessionmaker):
        mock_session = mock.MagicMock()
        mock_sessionmaker.return_value = mock_session

        mock_engine = mock.MagicMock()
        mock_sessionmaker_call = mock.call(bind=mock_engine)

        self.assertEqual(mock_session, models.sessionmaker(mock_engine))
        self.assertEqual(mock_sessionmaker.call_args, mock_sessionmaker_call)


class TestUser(unittest.TestCase):
    engine = create_engine('sqlite:///')
    sessionmaker = models.sessionmaker(engine=engine)

    @classmethod
    def setUpClass(cls):
        metadata.create_all(bind=cls.engine)

    def setUp(self):
        self.username = 'scott'
        self.password = 'tiger'
        self.email = 'scott@tiger.com'

    @classmethod
    def tearDownClass(cls):
        metadata.drop_all(bind=cls.engine)


class TestUserConstructor(TestUser):

    @mock.patch('db_models.User.hash_password')
    def test_constructor(self, mock_hash_function):

        mock_hash_function.return_value = 'hashed_password'

        user = models.User(self.username, self.password, self.email)
        self.assertIsInstance(user, models.User)
        self.assertEqual(user.username, self.username)
        self.assertEqual(user.email, self.email)
        self.assertEqual(user.password_hash, mock_hash_function.return_value)

        mock_hash_function_call = mock.call(self.password)
        self.assertEqual(mock_hash_function.call_args, mock_hash_function_call)


class TestHashPassword(TestUser):
    def setUp(self):
        TestUser.setUp(self)
        self.user = models.User(self.username, self.password, self.email)

    @mock.patch('db_models.pwd_context.encrypt')
    def test_hash_password(self, mock_encrypt):
        self.assertEqual(
            mock_encrypt.return_value, models.User.hash_password(self.password)
        )

        mock_encrypt_call = mock.call(self.password)
        self.assertEqual(
            mock_encrypt_call, mock_encrypt.call_args
        )


class TestVerifyPassword(TestUser):
    def setUp(self):
        TestUser.setUp(self)
        self.user = models.User(self.username, self.password, self.email)
        self.bad_password = 'invalid'

        self.assertNotEqual(self.password, self.bad_password)

    def test_verify_good_password(self):
        self.assertTrue(self.user.verify_password(self.password))

    def test_verify_bad_password(self):
        self.assertFalse(self.user.verify_password(self.bad_password))


class TestGenerateAuthToken(TestUser):
    def setUp(self):
        TestUser.setUp(self)
        self.user = models.User(self.username, self.password, self.email)
        self.mock_token = 'foobarbaz123456'

    @mock.patch('db_models.Serializer.dumps')
    def test_generate_auth_token(self, mock_serializer):
        mock_serializer.return_value = self.mock_token
        mock_dumps_call = mock.call({'id': self.user.id})

        self.assertEqual(self.mock_token, self.user.generate_auth_token())
        self.assertEqual(mock_dumps_call, mock_serializer.call_args)


class TestVerifyAuthToken(TestUser):
    def setUp(self):
        TestUser.setUp(self)
        self.user = models.User(self.username, self.password, self.email)
        self.mock_token ='foobarbaz123456'

        session = self.sessionmaker()

        try:
            session.add(self.user)
            session.commit()
        except:
            session.rollback()
            raise

    def tearDown(self):
        session = self.sessionmaker()
        user = session.query(models.User).filter_by(id=self.user.id).first()
        session.delete(user)
        try:
            session.commit()
        except:
            session.rollback()
            raise

    @mock.patch('db_models.Serializer.loads')
    def test_verify_token(self, mock_serializer):
        mock_serializer.return_value = {'id': self.user.id}
        returned_data = models.User.verify_auth_token(self.mock_token)

        self.assertEqual(self.user.id, returned_data)

    @mock.patch('db_models.Serializer.loads')
    def test_verify_token_signature_expired(self, mock_serializer):
        mock_serializer.side_effect = models.SignatureExpired('test_error')

        self.assertIsNone(models.User.verify_auth_token(self.mock_token))

    @mock.patch('db_models.Serializer.loads')
    def test_verify_token_bad_signature(self, mock_serializer):
        mock_serializer.side_effect = models.BadSignature('test_error')
        self.assertIsNone(models.User.verify_auth_token(self.mock_token))
