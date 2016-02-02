"""
Contains unit tests for :mod:`json_schema.fields`
"""
from marshmallow import fields as marshmallow_fields
from json_schema import fields, schema
import unittest
import re

__author__ = 'Michal Kononenko'


class TestField(unittest.TestCase):
    def setUp(self):
        self.description = 'Test Description'


class TestDateTime(TestField):
    pass


class TestDateTimeConstructor(TestDateTime):

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

        self.assertEqual(expected_dict, self.datetime.json_schema)


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
            self.expected_dict, self.field.json_schema
        )


class TestString(TestField):
    def setUp(self):
        TestField.setUp(self)
        self.test_string = 'Test regex'
        self.regex_pattern = r'^%s' % self.test_string

        self.assertIsNotNone(re.search(self.regex_pattern, self.test_string))

        self.enum = [self.test_string]

        self.assertIn(self.test_string, self.enum)


class TestStringConstructor(TestString):
    def test_constructor_no_regex(self):
        field = fields.String(description=self.description)

        self.assertIsNone(field.regex)
        self.assertEqual(field.description, self.description)

    def test_constructor_with_regex(self):
        field = fields.String(description=self.description,
                              regex_pattern=self.regex_pattern)

        self.assertEqual(field.validators, [field._validate_against_regex])


class TestStringWithObject(TestString):
    def setUp(self):
        TestString.setUp(self)
        self.field = fields.String(
            description=self.description,
            regex_pattern=self.regex_pattern
        )


class TestValidateAgainstRegex(TestStringWithObject):
    def setUp(self):
        TestStringWithObject.setUp(self)
        self.bad_string = 'not a valid string'
        self.unmatched_string = '%s plus bad things'

    def test_validate_good_string(self):
        self.assertTrue(
            self.field._validate_against_regex(self.test_string)
        )

    def test_validate_bad_string(self):
        self.assertFalse(
            self.field._validate_against_regex(self.bad_string)
        )
        self.assertFalse(
            self.field._validate_against_regex(self.unmatched_string)
        )


class TestValidateEnum(TestString):
    def setUp(self):
        TestString.setUp(self)
        self.schema = fields.String(description=self.description,
                                    enum=self.enum)

    def test_validate_enum(self):
        self.assertTrue(self.schema._validate_enum(self.test_string))
        self.assertFalse(self.schema._validate_enum('Not a valid string'))


class TestStringSchema(TestStringWithObject):
    def setUp(self):
        TestStringWithObject.setUp(self)
        self.expected_dict = dict(
            description=self.description,
            pattern=self.regex_pattern,
            type=self.field.type
        )

    def test_schema(self):
        self.assertEqual(
            self.expected_dict, self.field.json_schema
        )


class TestNested(TestField):

    class SchemaToTest(schema.MarshmallowJSONSchema):
        data = fields.Integer()

    def setUp(self):
        TestField.setUp(self)
        self.schema_to_nest = self.SchemaToTest()
        self.valid_data = 1


class TestNestedConstructor(TestNested):
    def test_constructor(self):
        field = fields.Nested(
            self.schema_to_nest,
            description=self.description
        )
        self.assertEqual(field.description, self.description)
        self.assertTrue(field.strict)


class TestNestedWithObject(TestNested):
    def setUp(self):
        TestNested.setUp(self)
        self.field = fields.Nested(
            self.schema_to_nest,
            description=self.description
        )


class TestNestedJsonSchema(TestNestedWithObject):
    def setUp(self):
        TestNestedWithObject.setUp(self)
        self.expected_dict = dict(
            description=self.description,
            properties={"data": {"type": "integer"}},
            type=self.field.type
        )

    def test_json_schema(self):
        self.assertEqual(self.expected_dict,
                         self.field.json_schema)


class TestList(TestField):
    def setUp(self):
        TestField.setUp(self)
