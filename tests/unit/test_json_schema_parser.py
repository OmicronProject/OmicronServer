"""
Contains unit tests for :mod:`json_schema_parser`
"""
import unittest
import mock
from omicron_server import json_schema_parser as parser

__author__ = 'Michal Kononenko'

test_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "description": "Test schema for validator",
    "type": "object",
    "properties": {
        "test_string": {
            "type": "string",
            "pattern": "^[abc]",
        },
        "test_integer": {
            "type": "integer"
        }
    }
}


class TestJsonSchemaValidator(unittest.TestCase):

    def setUp(self):
        self.path = r'D:\test\this\is\not\a\real\path'
        with mock.patch(
            'omicron_server.json_schema_parser.JsonSchemaValidator'
            '._read_schema_from_file',
            return_value=test_schema
        ):
            with mock.patch('os.path.isfile', return_value=True):
                self.validator = parser.JsonSchemaValidator(self.path)


@mock.patch('os.path.isfile')
@mock.patch('omicron_server.json_schema_parser.JsonSchemaValidator'
            '._read_schema_from_file')
class TestJsonSchemaConstructor(unittest.TestCase):

    def setUp(self):
        self.path = r'D:\test\this\is\not\a\real\path'

    def test_file_not_found_error(self, mock_read, mock_isfile):
        mock_isfile.return_value = False

        mock_call = mock.call(self.path)

        with self.assertRaises(parser.FileNotFoundError):
            parser.JsonSchemaValidator(self.path)

        self.assertEqual(mock_call, mock_isfile.call_args)
        self.assertFalse(mock_read.called)

    @mock.patch('jsonschema.FormatChecker.conforms',
                return_value=False)
    def test_constructor_not_schema(self, mock_conforms, mock_read, mock_isfile):
        mock_isfile.return_value = True
        mock_isfile_call = mock.call(self.path)

        mock_read.return_value = test_schema
        mock_read_call = mock.call(self.path)

        with self.assertRaises(parser.BadJsonSchemaError):
            parser.JsonSchemaValidator(self.path)

        self.assertEqual(mock_read_call, mock_read.call_args)
        self.assertEqual(mock_isfile_call, mock_isfile.call_args)

        self.assertTrue(mock_conforms.called)

    @mock.patch('jsonschema.FormatChecker.conforms',
                return_value=True)
    def test_constructor(self, mock_conforms, mock_read, mock_isfile):
        mock_isfile.return_value = True
        mock_read.return_value = test_schema

        validator = parser.JsonSchemaValidator(self.path)
        self.assertIsInstance(validator, parser.JsonSchemaValidator)

        self.assertEqual(validator.path, self.path)

        self.assertTrue(mock_conforms.called)


class TestValidateDict(TestJsonSchemaValidator):

    def setUp(self):
        TestJsonSchemaValidator.setUp(self)
        self.dict_to_validate = {'test_string': 'abcd', 'test_integer': 1}
        self.bad_dict = {'test_string': 'z', 'test_integer': 'foo'}

    def test_validate_dict(self):
        self.assertTrue(self.validator.validate_dict(self.dict_to_validate)[0])

    def test_validate_bad_dict(self):
        self.assertFalse(self.validator.validate_dict(self.bad_dict)[0])
