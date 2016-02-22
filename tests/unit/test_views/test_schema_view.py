import unittest

import jsonschema
import mock

from omicron_server.views import SchemaDefinedResource

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


class TestAPIViewWithSchemaConstructor(TestAPIViewWithSchema):
    def setUp(self):
        self.view.show_schema = mock.MagicMock()
        self.view.get = mock.MagicMock()

    def test_view_constructor(self):
        self.view.__init__()
        self.assertTrue(self.view.show_schema.called)


class TestParseQueryString(TestAPIViewWithSchema):

    def test_parse_string_none_return_false(self):
        self.assertFalse(self.view._parse_query_string(None))

    def test_parse_query_string_returns_true(self):
        self.assertTrue(self.view._parse_query_string('true'))
        self.assertTrue(self.view._parse_query_string('True'))

    def test_parse_query_string_false_return(self):
        self.assertFalse(self.view._parse_query_string('false'))
        self.assertFalse(self.view._parse_query_string('False'))

    @mock.patch('views.schema_defined_resource.abort')
    def test_parse_query_string_404_abort(self, mock_abort):
        mock_abort_call = mock.call(404)

        self.view._parse_query_string('Should return 404')

        self.assertEqual(mock_abort_call, mock_abort.call_args)


class TestShowSchema(TestAPIViewWithSchema):

    @staticmethod
    def _method_to_decorate():
        return True

    @mock.patch('views.SchemaDefinedResource._parse_query_string',
                return_value=True)
    @mock.patch('views.schema_defined_resource.jsonify')
    def test_show_schema_true(self, mock_jsonify, mock_q_string):
        mock_request = mock.MagicMock()
        func = self.view.show_schema(self._method_to_decorate, mock_request)

        self.assertTrue(func())
        self.assertEqual(
            mock.call(self.view.schema),
            mock_jsonify.call_args
        )
        self.assertTrue(mock_q_string.called)
        self.assertTrue(mock_request.args.get.called)

    @mock.patch('views.SchemaDefinedResource._parse_query_string',
                return_value=False)
    @mock.patch('views.schema_defined_resource.jsonify')
    def test_show_schema_false(self, mock_jsonify, mock_parse):
        mock_request = mock.MagicMock()
        func = self.view.show_schema(self._method_to_decorate, mock_request)

        self.assertTrue(func())

        self.assertFalse(mock_jsonify.called)

        self.assertTrue(mock_parse.called)


class TestIsDraft3(TestAPIViewWithSchema):

    @mock.patch('views.schema_defined_resource.jsonschema.'
                'FormatChecker.conforms', return_value=True)
    def test_is_draft3(self, mock_conforms):
        self.assertTrue(self.view.is_schema_draft3)
        self.assertEqual(
            mock.call(self.view.schema, 'draft3'),
            mock_conforms.call_args
        )


class TestIsDraft4(TestAPIViewWithSchema):

    @mock.patch('views.schema_defined_resource.jsonschema.'
                'FormatChecker.conforms', return_value=True)
    def test_is_draft4(self, mock_conforms):
        self.assertTrue(self.view.is_schema_draft4)
        self.assertEqual(
            mock.call(self.view.schema, 'draft4'),
            mock_conforms.call_args
        )


class TestValidateSchema(TestAPIViewWithSchema):
    def setUp(self):
        self.valid_dict = {'entry': 'this is a string'}
        self.valid_dict_schema = {
            'entry':
                {'type': 'string', 'pattern': '/entry/'}
        }

    @mock.patch('views.schema_defined_resource.jsonschema.validate')
    def test_validate_dict_true(self, mock_validate):

        self.assertTrue(self.view.validate(self.valid_dict))
        self.assertEqual(
            mock.call(self.valid_dict, self.view.schema),
            mock_validate.call_args
        )

    @mock.patch('views.schema_defined_resource.jsonschema.validate',
                side_effect=jsonschema.ValidationError('test error'))
    def test_validate_dict_false(self, mock_validate):

        self.assertFalse(self.view.validate(self.valid_dict)[0])
        self.assertTrue(mock_validate.called)

    @mock.patch('views.schema_defined_resource.jsonschema.validate')
    def test_validate_dict_custom_schema(self, mock_validate):

        self.assertTrue(
                self.view.validate(self.valid_dict, self.valid_dict_schema)
        )

        self.assertEqual(
            mock.call(self.valid_dict, self.valid_dict_schema),
            mock_validate.call_args
        )
