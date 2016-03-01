import unittest
import jsonschema
import mock
from omicron_server.views import AbstractResource, SchemaDefinedResource

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
        self.assertFalse(self.view._should_show_schema(None))

    def test_parse_query_string_returns_true(self):
        self.assertTrue(self.view._should_show_schema('true'))
        self.assertTrue(self.view._should_show_schema('True'))

    def test_parse_query_string_false_return(self):
        self.assertFalse(self.view._should_show_schema('false'))
        self.assertFalse(self.view._should_show_schema('False'))

    @mock.patch('omicron_server.views.abstract_resource.abort')
    def test_parse_query_string_404_abort(self, mock_abort):
        mock_abort_call = mock.call(404)

        self.view._should_show_schema('Should return 404')

        self.assertEqual(mock_abort_call, mock_abort.call_args)


class TestShowSchema(TestAPIViewWithSchema):

    @staticmethod
    def _method_to_decorate():
        return True

    @mock.patch(
            'omicron_server.views.SchemaDefinedResource._should_show_schema',
            return_value=True)
    @mock.patch('omicron_server.views.abstract_resource.jsonify')
    @mock.patch('omicron_server.views.abstract_resource.request')
    def test_show_schema_true(self, mock_request, mock_jsonify, mock_q_string):
        func = self.view.show_schema(self._method_to_decorate)

        self.assertTrue(func())
        self.assertEqual(
            mock.call(self.view.schema),
            mock_jsonify.call_args
        )
        self.assertTrue(mock_q_string.called)
        self.assertTrue(mock_request.args.get.called)

    @mock.patch(
            'omicron_server.views.SchemaDefinedResource._should_show_schema',
            return_value=False)
    @mock.patch('omicron_server.views.abstract_resource.jsonify')
    @mock.patch('omicron_server.views.abstract_resource.request')
    def test_show_schema_false(self, mock_request, mock_jsonify, mock_parse):
        func = self.view.show_schema(self._method_to_decorate)

        self.assertTrue(func())

        self.assertFalse(mock_jsonify.called)

        self.assertTrue(mock_parse.called)


class TestValidateSchema(TestAPIViewWithSchema):
    def setUp(self):
        self.valid_dict = {'entry': 'this is a string'}
        self.valid_dict_schema = {
            'entry':
                {'type': 'string', 'pattern': '/entry/'}
        }

    @mock.patch(
            'omicron_server.views.abstract_resource.jsonschema.validate'
    )
    def test_validate_dict_true(self, mock_validate):

        self.assertTrue(self.view.validate(self.valid_dict))
        self.assertEqual(
            mock.call(self.valid_dict, self.view.schema),
            mock_validate.call_args
        )

    @mock.patch(
            'omicron_server.views.abstract_resource.jsonschema.validate',
            side_effect=jsonschema.ValidationError('test error')
    )
    def test_validate_dict_false(self, mock_validate):

        self.assertFalse(self.view.validate(self.valid_dict)[0])
        self.assertTrue(mock_validate.called)

    @mock.patch(
            'omicron_server.views.abstract_resource.jsonschema.validate'
    )
    def test_validate_dict_custom_schema(self, mock_validate):

        self.assertTrue(
                self.view.validate(self.valid_dict, self.valid_dict_schema)
        )

        self.assertEqual(
            mock.call(self.valid_dict, self.valid_dict_schema),
            mock_validate.call_args
        )
