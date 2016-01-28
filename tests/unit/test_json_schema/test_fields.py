"""
Contains unit tests for :mod:`json_schema.fields`
"""
from marshmallow import fields as marshmallow_fields
from json_schema import fields
import unittest

__author__ = 'Michal Kononenko'


class TestField(unittest.TestCase):
    pass


class TestDateTime(TestField):
    pass


class TestDateTimeConstructor(TestDateTime):
    def setUp(self):
        TestDateTime.setUp(self)
        self.description = 'Test Description'

    def test_constructor(self):
        date = fields.DateTime(description=self.description)

        self.assertIsInstance(date, marshmallow_fields.DateTime)
        self.assertEqual(date.description, self.description)