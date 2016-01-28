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


class TestInteger(TestField):
    def setUp(self):
        self.minimum = 0
        self.maximum = 2
        self.valid_integer = 1
        self.integer_too_big = 4
        self.integer_too_small = -1
        self.description = 'Test Description'


class TestIntegerConstructor(TestInteger):
    def test_constructor_default_args(self):
        integer_field = fields.Integer()
        self.assertIsNone(integer_field.description)
        self.assertIsNone(integer_field.minimum)
        self.assertIsNone(integer_field.maximum)

        self.assertEqual(integer_field.validators,
                         [integer_field._validate_quantity])

    def test_constructor_non_default_args(self):
        integer_field = fields.Integer(
            minimum=self.minimum, maximum=self.maximum,
            description=self.description
        )

        self.assertEqual(integer_field.minimum, self.minimum)
        self.assertEqual(integer_field.maximum, self.maximum)
        self.assertEqual(integer_field.description, self.description)


class TestIntegerWithObject(TestInteger):
    def setUp(self):
        TestInteger.setUp(self)
        self.field = fields.Integer(
            description=self.description,
            minimum=self.minimum,
            maximum=self.maximum
        )


class TestIntegerValidator(TestIntegerWithObject):
    def setUp(self):
        TestIntegerWithObject.setUp(self)
        self.assertLess(self.integer_too_small, self.minimum)
        self.assertGreater(self.integer_too_big, self.maximum)

    def test_validator_integer_too_small(self):
        with self.assertRaises(fields.ValidationError):
            self.field._validate_quantity(self.integer_too_small)

    def test_validator_integer_too_big(self):
        with self.assertRaises(fields.ValidationError):
            self.field._validate_quantity(self.integer_too_big)

    def test_validator_integer_correct(self):
        self.assertTrue(
                self.field._validate_quantity(self.valid_integer)
        )


class TestIntegerSchema(TestIntegerWithObject):
    def setUp(self):
        TestIntegerWithObject.setUp(self)
        self.expected_dict = dict(
            type=self.field.type,
            description=self.description,
            exclusiveMinimum=self.minimum,
            exclusiveMaximum=self.maximum
        )

    def test_schema(self):
        self.assertEqual(
            self.expected_dict, self.field.schema
        )