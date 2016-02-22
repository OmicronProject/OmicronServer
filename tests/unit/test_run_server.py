"""
Contains unit tests for :mod:`run_server`
"""
import unittest
import mock
import omicron_server.run_server as run_server
import logging
from database import Administrator
from config import Config

from omicron_server import run_server
from omicron_server.database import Administrator

__author__ = 'Michal Kononenko'

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class TestSetLogFile(unittest.TestCase):
    """
    Tests that if a logfile path is provided, that the master
    application log will log data to the filename given
    """
    def setUp(self):
        self.logfile_name = 'logfile'

        self.mock_conf = Config()
        self.mock_conf.LOGFILE = self.logfile_name

    @mock.patch('logging.basicConfig')
    def test_logging(self, mock_basic_config):
        expected_config_call = mock.call(filename=self.logfile_name)

        run_server.set_logfile(self.mock_conf)

        self.assertEqual(expected_config_call, mock_basic_config.call_args)

    @mock.patch('logging.basicConfig')
    def test_logging_no_logfile(self, mock_config):
        mock_conf = self.mock_conf
        mock_conf.LOGFILE = None
        run_server.set_logfile(mock_conf)

        self.assertFalse(mock_config.called)


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
    def test_create_root_user_not_found(self, mock_add, mock_first):
        mock_first.return_value = None
        run_server.create_root_user()

        self.assertTrue(mock_first.called)
        self.assertTrue(mock_add.called)
