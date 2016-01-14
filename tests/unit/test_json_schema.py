"""
Contains unit tests for :mod:`json_schema`
"""
import unittest
import json_schema

__author__ = 'Michal Kononenko'

description = 'Test Description'
minimum = 3
maximum = 10


class SchemaForTesting(json_schema.MarshmallowJSONSchema):
    test_field = json_schema.Integer(
            description, minimum=minimum, maximum=maximum
    )


class TestLoading(unittest.TestCase):
    def setUp(self):
        self.schema = SchemaForTesting()

    def test_load_min(self):
        value = 1
        with self.assertRaises(json_schema.ValidationError):
            self.schema.load(dict(test_field=value))

    def test_load_over_max(self):
        value = 100
        with self.assertRaises(json_schema.ValidationError):
            self.schema.load(dict(test_field=value))