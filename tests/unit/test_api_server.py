"""
Contains unit tests for :mod:`api_server`
"""
import uuid

import mock
from flask import jsonify
from sqlalchemy import create_engine

from omicron_server import api_server
from omicron_server.database.sessions import ContextManagedSession
from tests import TestCaseWithAppContext

__author__ = 'Michal Kononenko'

test_engine = create_engine('sqlite:///')


class TestGetRequestGuid(TestCaseWithAppContext):
    def setUp(self):
        TestCaseWithAppContext.setUp(self)
        self.request_id = uuid.uuid1()

    @mock.patch('omicron_server.api_server.uuid1')
    def test_get_id(self, mock_guid_maker):
        mock_guid_maker.return_value = self.request_id
        api_server.setup_request()
        self.assertEqual(
            api_server.g.request_id,
            str(self.request_id)
        )


class TestAddRequestGuidToHeader(TestCaseWithAppContext):
    def setUp(self):
        TestCaseWithAppContext.setUp(self)
        self.response = jsonify({'message': 'test'})
        self.request_id = str(uuid.uuid1())

        api_server.g.request_id = self.request_id
        api_server.g.session = mock.MagicMock()

    def tearDown(self):
        del api_server.g.request_id
        TestCaseWithAppContext.tearDown(self)

    def test_add(self):
        response = api_server.teardown_request(self.response)
        self.assertEqual(
            response.headers['Request-Id'],
            self.request_id
        )

        self.assertTrue(api_server.g.session.close.called)


class TestHelloWorld(TestCaseWithAppContext):
    """
    Tests :meth:`api_server.hello_world`
    """
    def setUp(self):
        TestCaseWithAppContext.setUp(self)
        api_server.database_session = ContextManagedSession(bind=test_engine)
        self.app = api_server.app
        self.client = self.app.test_client()
        self.request_method = self.client.get
        self.url = '/'

        self.headers = {'content-type': 'application/json'}

    def test_hello_world(self):
        """
        Tests that a request to the server's root endpoint returns 200,
        indicating that the server has set up and is running successfully.
        """
        r = self.request_method(self.url, headers=self.headers)
        self.assertEqual(r.status_code, 200)
