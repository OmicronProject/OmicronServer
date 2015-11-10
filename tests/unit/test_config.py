import unittest
import mock
from config import Config

__author__ = 'Michal Kononenko'

environment = {'DATABASE_URL': 'some_postgres_address'}


class TestConfigConstructor(unittest.TestCase):

    def test_config(self):
        conf = Config(conf_dict=environment)

        self.assertEqual(conf.DATABASE_URL, environment['DATABASE_URL'])