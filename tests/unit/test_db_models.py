"""
Contains unit tests for :mod:`db_models`
"""
import unittest
import unittest.mock as mock
import db_models as models
from sqlalchemy import create_engine
from db_schema import metadata

__author__ = 'Michal Kononenko'


class TestContextManagedSession(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///')
        self.base_session = models.ContextManagedSession(bind=self.engine)

    def test_context_managed_session_enter(self):
        with self.base_session as session:
            self.assertNotEqual(self.base_session, session)
            self.assertEqual(self.base_session.__dict__, session.__dict__)

    def test_exit_no_error(self):
        commit = mock.MagicMock()
        rollback = mock.MagicMock()
        with self.base_session as session:
            session.commit = commit
            session.rollback = rollback

        self.assertFalse(rollback.called)
        self.assertEqual(commit.call_args, mock.call())

    def test_exit_with_error(self):
        error_to_raise = Exception('test_error')
        commit = mock.MagicMock()
        rollback = mock.MagicMock()

        with self.assertRaises(error_to_raise.__class__):
            with self.base_session as session:
                session.commit = commit
                session.rollback = rollback
                raise Exception('test_error')

        self.assertFalse(commit.called)
        self.assertEqual(rollback.call_args, mock.call())

    def test_exit_commit_error(self):
        error_to_raise = Exception('test_error')
        commit = mock.MagicMock(side_effect=error_to_raise)
        rollback = mock.MagicMock()

        with self.assertRaises(error_to_raise.__class__):
            with self.base_session as session:
                session.commit = commit
                session.rollback = rollback

        self.assertTrue(commit.called)
        self.assertTrue(rollback.called)

    def test_repr(self):
        repr_string = '%s(bind=%s, expire_on_commit=%s)' % \
                      (self.base_session.__class__.__name__,
                       self.base_session.bind,
                       self.base_session.expire_on_commit)

        self.assertEqual(repr_string, self.base_session.__repr__())


class TestSessionDecorator(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///')
        self.base_session = models.ContextManagedSession(bind=self.engine)

    def test_decorator_callable(self):
        @self.base_session()
        def _test_decorator(created_session):
            return created_session

        session = _test_decorator()
        self.assertIsInstance(session, models.ContextManagedSession)
        self.assertNotEqual(session, self.base_session)


class TestSessionMaker(unittest.TestCase):

    def test_sessionmaker_with_engine(self):
        engine = mock.MagicMock()
        session = models.sessionmaker(engine=engine)
        self.assertEqual(session.bind, engine)


class TestUser(unittest.TestCase):
    engine = create_engine('sqlite:///')

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
        self.assertEqual(user.email_address, self.email)
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

        with models.sessionmaker(self.engine) as session:
            session.add(self.user)

    def tearDown(self):
        with models.sessionmaker(self.engine) as session:
            user = session.query(models.User).\
                filter_by(id=1).first()
            session.delete(user)

    @mock.patch('db_models.Serializer.loads')
    def test_verify_token(self, mock_serializer):
        mock_serializer.return_value = {'id': 1}
        returned_data = models.User.verify_auth_token(self.mock_token)

        self.assertEqual(1, returned_data)

    @mock.patch('db_models.Serializer.loads')
    def test_verify_token_signature_expired(self, mock_serializer):
        mock_serializer.side_effect = models.SignatureExpired('test_error')

        self.assertIsNone(models.User.verify_auth_token(self.mock_token))

    @mock.patch('db_models.Serializer.loads')
    def test_verify_token_bad_signature(self, mock_serializer):
        mock_serializer.side_effect = models.BadSignature('test_error')
        self.assertIsNone(models.User.verify_auth_token(self.mock_token))


class TestGet(TestUser):
    def setUp(self):
        TestUser.setUp(self)
        self.user = models.User(self.username, self.password, self.email)
        self.expected_result = {
            'username': self.username,
            'email': self.email
        }

    def test_get(self):
        self.assertEqual(self.expected_result, self.user.get)
