"""
Contains unit tests for :mod:`json_schema`
"""
import unittest
import mock
import json_schema

__author__ = 'Michal Kononenko'


class TestMarshmallowJSONSchema(unittest.TestCase):
    def setUp(self):
        self.schema_title = 'Test Schema'
        self.schema_description = 'Test Description'


class TestMarshmallowJSONSchemaConstructor(TestMarshmallowJSONSchema):

    @mock.patch('marshmallow.Schema.__init__')
    def test_constructor(self, mock_init):

        schema = json_schema.MarshmallowJSONSchema()
        expected_call = mock.call(schema, strict=True)

        self.assertEqual(expected_call, mock_init.call_args)


class TestSchemaRequiredFields(TestMarshmallowJSONSchema):
    class SchemaToTest(json_schema.MarshmallowJSONSchema):
        field = json_schema.Integer(required=True)

    def setUp(self):
        TestMarshmallowJSONSchema.setUp(self)
        self.schema = self.SchemaToTest()
        self.data_to_load = {'field': 1}

    def test_required(self):
        self.assertEqual(self.schema.required_fields, ['field'])


class TestSchemaDisplayMethod(TestMarshmallowJSONSchema):
    class SchemaToTest(json_schema.MarshmallowJSONSchema):
        field = json_schema.Integer(required=True)

    def setUp(self):
        TestMarshmallowJSONSchema.setUp(self)
        self.schema = self.SchemaToTest()
