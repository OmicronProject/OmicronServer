"""
Contains unit tests for :mod:`run_server`
"""
import unittest
import mock
import run_server
import logging
from database import Administrator

__author__ = 'Michal Kononenko'

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class TestRunServer(unittest.TestCase):
    """
    Contains unit tests for the script
    """
    def setUp(self):
        self.command_to_run = 'python ../../run_server.py'
        self.user = Administrator('root', 'root', 'scott@deler.com')


class TestCreateRootUser(TestRunServer):

    @mock.patch('sqlalchemy.orm.Query.first')
    @mock.patch('sqlalchemy.orm.Session.add')
    def test_create_root_user_found(self, mock_add, mock_first):
        mock_first.return_value = self.user
        run_server.create_root_user()

        self.assertTrue(mock_first.called)
        self.assertFalse(mock_add.called)

    @mock.patch('sqlalchemy.orm.Query.first')
    @mock.patch('sqlalchemy.orm.Session.add')
    def test_create_root_user_found(self, mock_add, mock_first):
        mock_first.return_value = None
        run_server.create_root_user()

        self.assertTrue(mock_first.called)
        self.assertTrue(mock_add.called)
