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
    def setUp(self):
        self.description = 'Test Description'


class TestDateTimeConstructor(TestDateTime):
    def setUp(self):
        TestDateTime.setUp(self)

    def test_constructor(self):
        date = fields.DateTime(description=self.description)

        self.assertIsInstance(date, marshmallow_fields.DateTime)
        self.assertEqual(date.description, self.description)

    def test_constructor_default_args(self):
        date = fields.DateTime()
        self.assertIsNone(date.description)


class TestDateTimeWithObject(TestDateTime):
    def setUp(self):
        TestDateTime.setUp(self)
        self.datetime = fields.DateTime(description=self.description)


class TestDateTimeSchema(TestDateTimeWithObject):
    def setUp(self):
        TestDateTimeWithObject.setUp(self)
        self.expected_type = 'string'
        self.expected_format = 'date-time'

    def test_schema(self):
        expected_dict = dict(
                type=self.expected_type, format=self.expected_format,
                description=self.description
        )

        self.assertEqual(expected_dict, self.datetime.schema)