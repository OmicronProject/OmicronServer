import unittest
import mock
from config import Config

__author__ = 'Michal Kononenko'

environment = {'DATABASE_URL': 'some_postgres_address'}


@mock.patch('config.Config.update_alembic_ini')
class TestConfigConstructor(unittest.TestCase):

    def test_config(self, mock_update):
        conf = Config(conf_dict=environment)

        self.assertEqual(conf.DATABASE_URL, environment['DATABASE_URL'])
        self.assertTrue(mock_update.called)