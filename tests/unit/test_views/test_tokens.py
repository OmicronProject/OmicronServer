"""
Contains unit tests for :mod:`omicron_server.views.tokens`
"""
from tests import TestCaseWithAppContext, TestCaseWithDatabase
import mock
from omicron_server.auth import _verify_user
from omicron_server.views import tokens
from omicron_server.database import User, Administrator, ContextManagedSession
from uuid import uuid1
from omicron_server.config import default_config as conf
from contextlib import contextmanager
from datetime import datetime

__author__ = 'Michal Kononenko'


class TestTokens(TestCaseWithDatabase):
    def setUp(self):
        TestCaseWithAppContext.setUp(self)
        self.endpoint = tokens.Tokens()
        self.token_string = str(uuid1())

        self.username = 'username'
        self.password = 'password'
        self.email = 'scott@tiger.com'

        self.user = User(self.username, self.password, self.email)
        self.admin = Administrator(self.username, self.password, self.email)


@mock.patch('omicron_server.views.tokens.g')
@mock.patch('omicron_server.auth._verify_user', return_value=True)
@mock.patch('omicron_server.views.tokens.database_session')
@mock.patch(
        'omicron_server.views.tokens.Tokens._authenticated_from_token_response'
)
@mock.patch('omicron_server.views.tokens.Tokens._successful_response')
class TestPost(TestTokens):

    def setUp(self):
        TestTokens.setUp(self)
        self.expiration = 1500

        self.user.generate_auth_token = mock.MagicMock(
            return_value=(self.token_string, self.expiration)
        )

        self.endpoint._successful_response = mock.MagicMock()

    def test_post_authenticated_from_token(
            self, mock_response, mock_error, mock_session, mock_auth, mock_g
    ):
        mock_g.authenticated_from_token = True
        mock_g.user = self.user

        self.user.generate_auth_token = mock.MagicMock()

        self.assertEqual(mock_error, self.endpoint.post())

        self.assertFalse(mock_session.query.called)
        self.assertFalse(mock_response.called)
        self.assertTrue(mock_auth.called)

    @mock.patch('omicron_server.views.tokens.request')
    def test_post_non_default_expiration_time(
            self, mock_request, mock_response, mock_error, mock_session,
            mock_auth, mock_g
    ):
        mock_request.args.get = mock.MagicMock(
                return_value=self.expiration
        )
        mock_g.authenticated_from_token = False
        mock_g.user = self.user

        response = self.endpoint.post()

        self.assertEqual(
                response, self.endpoint._successful_response.return_value
        )

        self.assertEqual(
            mock.call(self.token_string, self.expiration),
            self.endpoint._successful_response.call_args
        )

        self.assertTrue(mock_request.args.get.called)
        self.assertTrue(self.user.generate_auth_token.called)

    @mock.patch('omicron_server.views.tokens.request')
    def test_post_no_argument_provided(
        self, mock_request, mock_response, mock_error, mock_session,
        mock_auth, mock_g
    ):
        mock_g.authenticated_from_token = False
        mock_g.user = self.user

        self.user.generate_auth_token = mock.MagicMock(
            return_value=(
                self.token_string,
                conf.DEFAULT_TOKEN_EXPIRATION_TIME,
            )
        )

        mock_request.args.get = mock.MagicMock(
            side_effect=TypeError('The expiration is bad')
        )

        response = self.endpoint.post()

        self.assertEqual(
                response, self.endpoint._successful_response.return_value
        )

        self.assertEqual(
            self.endpoint._successful_response.call_args,
            mock.call(self.token_string, conf.DEFAULT_TOKEN_EXPIRATION_TIME)
        )


@mock.patch('omicron_server.auth._verify_user', spec=_verify_user,
            return_value=True)
@mock.patch('omicron_server.views.tokens.g')
@mock.patch('sqlalchemy.orm.Query.first')
class TestDelete(TestTokens):
    def setUp(self):
        TestTokens.setUp(self)
        self.session = mock.MagicMock(
            spec=ContextManagedSession()
        )

        self.token = mock.MagicMock()

        self.endpoint.make_400_error_response = mock.MagicMock()
        self.error_message = 'This is an error'

    @contextmanager
    def _prepare_tests(self, mock_first, mock_g, mock_auth):
        mock_auth.return_value = True
        mock_g.authenticated_from_token = True
        mock_g.token_string = self.token_string
        mock_first.return_value = self.token

        yield

        self.assertTrue(mock_auth.called)

    def test_delete_administrator(self, mock_first, mock_g, mock_auth):
        with self._prepare_tests(mock_first, mock_g, mock_auth):
            mock_g.user = self.admin
            response = self.endpoint.delete()

        self.assertEqual(response.status_code, 200)

    def test_delete_user(self, mock_first, mock_g, mock_auth):
        with self._prepare_tests(mock_first, mock_g, mock_auth):
            mock_g.user = self.user
            response = self.endpoint.delete()

        self.assertEqual(response.status_code, 200)

    def test_delete_no_token(self, mock_first, mock_g, mock_auth):
        mock_first.return_value = None
        mock_g.user = self.user
        mock_g.token_string = self.token_string
        mock_auth.return_value = True

        mock_response = mock.MagicMock()

        self.endpoint.make_400_error_response = mock_response

        response = self.endpoint.delete()

        self.assertEqual(response, mock_response.return_value)
        self.assertTrue(mock_response.called)

    def test_delete_token_processing_error(
            self, mock_first, mock_g, mock_auth
    ):
        with self._prepare_tests(mock_first, mock_g, mock_auth):
            self.endpoint.get_token_string = mock.MagicMock(
                side_effect=self.endpoint.TokenProcessingError(
                        self.error_message
                )
            )

            self.endpoint.delete()
            self.assertTrue(self.endpoint.get_token_string.called)
            self.assertTrue(self.endpoint.make_400_error_response.called)


class TestSuccessfulResponse(TestTokens):
    def setUp(self):
        TestTokens.setUp(self)
        self.expiration_date = datetime.utcnow()

    def test_response(self):
        self.assertEqual(
            self.endpoint._successful_response(
                    self.token_string, self.expiration_date
            ).status_code,
            201
        )


class TestAuthedFromTokenError(TestTokens):
    def test_error(self):
        self.assertEqual(
                self.endpoint._authenticated_from_token_response.status_code,
                403
        )


@mock.patch('omicron_server.views.tokens.g')
class TestGetTokenString(TestTokens):
    def setUp(self):
        TestTokens.setUp(self)
        self.request = mock.MagicMock()

    def test_authenticated_from_token(self, mock_g):
        mock_g.authenticated_from_token = True
        mock_g.token_string = self.token_string

        token = self.endpoint.get_token_string(self.request)
        self.assertEqual(token, self.token_string)

    def test_request_not_json(self, mock_g):
        mock_g.authenticated_from_token = False
        self.request.json = None

        with self.assertRaises(self.endpoint.TokenProcessingError):
            self.endpoint.get_token_string(self.request)

    def test_key_not_found_in_json(self, mock_g):
        mock_g.authenticated_from_token = False
        self.request.json = {'bad key': 'bad value'}

        with self.assertRaises(self.endpoint.TokenProcessingError):
            self.endpoint.get_token_string(self.request)

    def test_happy_path(self, mock_g):
        mock_g.authenticated_from_token = False
        self.request.json = {'token': self.token_string}

        self.assertEqual(
            self.token_string,
            self.endpoint.get_token_string(self.request)
        )


class TestMake400Response(TestTokens):
    def setUp(self):
        TestTokens.setUp(self)
        self.message = 'This is an error message'

    @mock.patch('omicron_server.views.tokens.jsonify')
    def test_make_response(self, mock_jsonify):
        response = self.endpoint.make_400_error_response(self.message)

        self.assertEqual(
            mock.call({'error': self.message}),
            mock_jsonify.call_args
        )

        self.assertEqual(response.status_code, 400)
