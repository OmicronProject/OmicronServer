"""
Contains tests for the API
"""
import unittest
from omicron_server import app

__author__ = 'Michal Kononenko'


class TestCaseWithAppContext(unittest.TestCase):
    def setUp(self):
        self.context = app.test_request_context()
        self.context.push()

    def tearDown(self):
        self.context.pop()
