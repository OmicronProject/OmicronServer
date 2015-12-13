import unittest
import mock
from api_views.schema_defined_resource import SchemaDefinedResource
from flask import request

__author__ = 'Michal Kononenko'


class Resource(SchemaDefinedResource):
    schema = {
      "$schema": "http://json-schema.org/draft-04/schema#",
      "id": "http://jsonschema.net",
      "type": "object",
      "properties": {
        "entry": {
          "id": "http://jsonschema.net/entry",
          "type": "string"
        }
      },
      "required": [
        "entry"
      ]
    }


class TestAPIViewWithSchema(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.view = Resource()


class TestParseSchemaRequestParams(TestAPIViewWithSchema):

    def setUp(self):
        self.flask_request = mock.MagicMock(spec=request)
        self.flask_request.args = mock.MagicMock()

    @mock.patch('api_views.schema_defined_resource.SchemaDefinedResource._parse_query_string',
                return_value=True)
    def test_parse_schema_request_params(self, mock_parse_q_string):

        new_tuple = self.view._parse_schema_request_params(self.flask_request)

        self.assertIsInstance(new_tuple, self.view.__request_params__)


class TestParseQueryString(TestAPIViewWithSchema):

    def test_parse_string_none_return_false(self):
        self.assertFalse(self.view._parse_query_string(None))

    def test_parse_query_string_returns_true(self):
        self.assertTrue(self.view._parse_query_string('true'))
        self.assertTrue(self.view._parse_query_string('True'))

    def test_parse_query_string_false_return(self):
        self.assertFalse(self.view._parse_query_string('false'))
        self.assertFalse(self.view._parse_query_string('False'))

    @mock.patch('api_views.schema_defined_resource.abort')
    def test_parse_query_string_404_abort(self, mock_abort):
        mock_abort_call = mock.call(404)

        self.view._parse_query_string('Should return 404')

        self.assertEqual(mock_abort_call, mock_abort.call_args)


class TestShowSchema(TestAPIViewWithSchema):

    @staticmethod
    def _method_to_decorate():
        return True

    def setUp(self):
        self.view._parse_schema_request_params = mock.MagicMock()

    @mock.patch('api_views.schema_defined_resource.SchemaDefinedResource._parse_schema_request_params')
    def test_show_schema_no_q_params(self, mock_parse):
        mock_parse.return_value = self.view.__request_params__(False, False)
        func = self.view.show_schema(self._method_to_decorate)

        self.assertTrue(func())
