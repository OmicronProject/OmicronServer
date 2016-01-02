"""
Contains unit tests for :mod:`views`
"""
import json
import logging
import unittest
from base64 import b64encode

import mock
from sqlalchemy import create_engine

import views.users as users
from api_server import app
from database.schema import metadata
from database.models.users import User
from database.sessions import ContextManagedSession

__author__ = 'Michal Kononenko'

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

test_engine = create_engine('sqlite:///')
users.database_session = ContextManagedSession(bind=test_engine)


class TestView(unittest.TestCase):
    """
    Contains generic set-up for each view
    """
    @classmethod
    def setUpClass(cls):
        """
        Set up the test client
        :return:
        """
        cls.client = app.test_client(use_cookies=True)
        cls.headers = {'content-type': 'application/json'}
        metadata.create_all(bind=test_engine)

    @classmethod
    def tearDownClass(cls):
        metadata.drop_all(bind=test_engine)


class TestRenderWelcomePage(TestView):
    def setUp(self):
        self.request_method = self.client.get

    def test_page(self):
        self.assertEqual(self.request_method('/').status_code, 200)


class TestUserContainer(TestView):
    @classmethod
    def setUpClass(cls):
        TestView.setUpClass()
        cls.username = 'scott'
        cls.password = 'tiger'
        cls.email = 'scott@tiger.com'


class TestParseSearchQueryParams(TestUserContainer):

    def setUp(self):
        TestUserContainer.setUp(self)
        self.request_method = self.client.get
        self.template_url = 'api/v1/users'

        user = User(self.username, self.password, self.email)

        with users.database_session as session:
            session.add(user)

        self.top_level_json_key = 'users'
        self.api_charset = 'utf-8'

    def tearDown(self):

        with users.database_session as session:
            user = session.query(User).filter_by(
                username=self.username
            ).first()

            session.delete(user)

    def test_contains_match_user(self):
        contains_string = self.username[1:-1]
        request_url = '%s?contains=%s' % (self.template_url, contains_string)

        json_dict = self._get_request(request_url, 1)

        self.assertTrue(json_dict[self.top_level_json_key])

    def test_contains_user_not_found(self):
        contains_string = 'abc'
        self.assertNotIn(contains_string, self.username)

        request_url = '%s?contains=%s' % (self.template_url, contains_string)

        json_dict = self._get_request(request_url, 0)

        self.assertFalse(json_dict[self.top_level_json_key])

    def test_begins_with_user_found(self):
        begins_with_string = self.username[0:2]
        request_url = '%s?starts_with=%s' % (
            self.template_url, begins_with_string
        )

        json_dict = self._get_request(request_url, 1)

        self.assertTrue(json_dict[self.top_level_json_key])

    def test_begins_with_user_not_found(self):
        begins_with_string = 'y'

        self.assertNotIn(begins_with_string, self.username)

        request_url = '%s?starts_with=%s' % (
            self.template_url, begins_with_string
        )

        json_dict = self._get_request(request_url, 0)

        self.assertFalse(json_dict[self.top_level_json_key])

    def test_ends_with_user_found(self):
        ends_with_string = self.username[-1:-3]

        request_url = '%s?ends_with=%s' % (
            self.template_url, ends_with_string
        )

        json_dict = self._get_request(request_url, 1)

        self.assertTrue(json_dict[self.top_level_json_key])

    def test_ends_with_user_not_found(self):
        ends_with_string = 'a'

        self.assertNotIn(ends_with_string, self.username)

        request_url = '%s?ends_with=%s' % (
            self.template_url, ends_with_string
        )

        json_dict = self._get_request(request_url, 0)

        self.assertFalse(json_dict[self.top_level_json_key])

    def test_empty_search_string(self):
        request_url = self.template_url

        self._get_request(request_url, 1)

    def _get_request(self, request_url, expected_count):
        r = self.request_method(request_url, headers=self.headers)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(int(r.headers['Count']), expected_count)

        json_dict = json.loads(r.data.decode(self.api_charset))

        return json_dict


@mock.patch('sqlalchemy.orm.Session.add')
class TestCreateUser(TestUserContainer):
    def setUp(self):
        self.request_method = self.client.post
        self.url = 'api/v1/users'

    def test_post(self, mock_add):
        data_to_post = {
            'username': self.username,
            'password': self.password,
            'email': self.email
        }

        r = self.request_method(self.url, data=json.dumps(data_to_post),
                                headers=self.headers)
        self.assertEqual(r.status_code, 201)

        self.assertTrue(mock_add.called)

    def test_post_bad_data(self, mock_add):
        data_to_post = {
            'user': self.username,
            'password': self.password,
            'email': self.email
        }
        r = self.request_method(self.url, data=json.dumps(data_to_post),
                                headers=self.headers)
        self.assertEqual(r.status_code, 400)
        self.assertFalse(mock_add.called)


class TestUserView(TestView):

    def setUp(self):
        self.username = 'scott'
        self.password = 'tiger'
        self.email = 'scott@tiger.com'
        self.user = User(self.username, self.password, self.email)


class TestGet(TestUserView):

    def setUp(self):
        TestUserView.setUp(self)
        self.request_method = self.client.get
        self.url = 'api/v1/users/%s' % self.username
        self.headers['Authorization'] = 'Basic %s' % \
            b64encode(('%s:%s' % (self.username, self.password)).encode('ascii')).decode('ascii')

        self.bad_user = User('foo', 'bar', 'foo@bar.com')

    @mock.patch('sqlalchemy.orm.Query.first')
    @mock.patch('views.users.auth.login_required')
    @mock.patch('views.users.g')
    def test_get_correct(self, mock_g, mock_auth, mock_first):
        mock_auth.return_value = lambda f: f
        mock_first.return_value = self.user

        mock_g.user = self.user

        r = self.request_method(self.url, headers=self.headers)
        self.assertEqual(r.status_code, 200)

        self.assertTrue(mock_first.called)

    @mock.patch('sqlalchemy.orm.Query.first')
    @mock.patch('views.users.auth.login_required')
    @mock.patch('views.users.g')
    def test_get_fake_user(self, mock_g, mock_auth, mock_first):
        mock_auth.return_value = lambda f: f
        mock_first.return_value = self.user

        mock_g.user = self.bad_user

        r = self.request_method(self.url, headers=self.headers)
        self.assertEqual(r.status_code, 401)

        self.assertTrue(mock_first.called)
