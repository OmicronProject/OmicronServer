"""
Contains unit tests for :mod:`omicron_server.views.tokens`
"""
from tests import TestCaseWithAppContext
import mock
from omicron_server.views import tokens
from omicron_server.database import User, Administrator

__author__ = 'Michal Kononenko'


class TestTokens(TestCaseWithAppContext):
    def setUp(self):
        TestCaseWithAppContext.setUp(self)
        self.endpoint = tokens.Tokens()
        self.username = 'username'
        self.password = 'password'
        self.email = 'scott@tiger.com'

        self.user = User(self.username, self.password, self.email)
        self.admin = Administrator(self.username, self.password, self.email)


@mock.patch('omicron_server.views.tokens.g')
@mock.patch('omicron_server.auth._verify_user', return_value=True)
@mock.patch('omicron_server.views.tokens.database_session')
@mock.patch('omicron_server.views.tokens.Tokens._authed_from_token_error')
class TestPost(TestTokens):

    def test_post_authenticated_from_token(
            self, mock_error, mock_session, mock_auth, mock_g
    ):
        mock_g.authenticated_from_token = True
        mock_g.user = self.user

        self.user.generate_auth_token = mock.MagicMock()

        self.assertEqual(mock_error, self.endpoint.post())

        self.assertFalse(mock_session.query.called)
