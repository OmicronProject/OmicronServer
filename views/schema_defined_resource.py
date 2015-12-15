import abc
import json
import jsonschema
from collections import namedtuple
from functools import wraps
from flask import request, jsonify, abort
from flask.ext.restful import Resource

__author__ = 'Michal Kononenko'


class SchemaDefinedResource(Resource):
    """
    Abstract class that defines an API view with a schema
    built into it. This class is capable of serving its schema
    and
    """

    __request_params__ = namedtuple(
            'RequestParams', ['show_schema', 'show_data']
    )
    _http_method_list = [
        'get', 'post', 'put', 'patch', 'delete', 'options', 'head'
    ]

    @classmethod
    def _parse_schema_request_params(cls, flask_request):
        """
        Take in parameters from the Flask request and determine if
        the schema or data need to be shown
        :param flask_request: The :attr:`Flask.request` that needs to be
            parsed
        :return: A named tuple consisting of two booleans, one
            whether to show the schema and one to determine whether
            to show the underlying data in the endpoint
        """

        return cls.__request_params__(
            cls._parse_query_string(flask_request.args.get('schema')),
            cls._parse_query_string(flask_request.args.get('show_data'))
        )

    @staticmethod
    def _parse_query_string(string):
        if string is None:
            return False
        if string == 'true' or string == 'True':
            return True
        elif string == 'false' or string == 'False':
            return False
        else:
            abort(404)

    @classmethod
    def show_schema(cls, f):
        request_params = cls._parse_schema_request_params(request)

        @wraps(f)
        def _wrapper(*args, **kwargs):
            if not request_params.show_schema and not request_params.show_data:
                return f(*args, **kwargs)
            elif not request_params.show_schema and request_params.show_data:
                return f(*args, **kwargs)
            elif request_params.show_schema and not request_params.show_data:
                return jsonify(cls.schema)
            elif request_params.show_schema and request_params.show_data:
                response = f(*args, **kwargs)

                response_dict = json.loads(response.data)

                dict_to_return = dict(schema=cls.schema, **response_dict)

                return jsonify(dict_to_return), response.status_code

        return _wrapper

    @staticmethod
    @abc.abstractproperty
    def schema():
        """
        Return the JSON schema of the view as a dictionary
        """
        raise NotImplementedError

    @property
    def is_schema_draft3(self):
        """
        Checks if :attr:`self.schema` corresponds to the Draft 3
        JSON Schema

        .. note ::

            At the time of writing, the latest draft of JSON Schema
            is Draft 4. Refrain from using Draft 3 schemas in this API
            wherever possible

        :return: True if the schema conforms to draft 3, else false
        :rtype: bool
        """
        format_checker = jsonschema.FormatChecker()
        return format_checker.conforms(self.schema, 'draft3')

    @property
    def is_schema_draft4(self):
        format_checker = jsonschema.FormatChecker()
        return format_checker.conforms(self.schema, 'draft4')

    def validate(self, dict_to_validate, source_dict=None):
        """
        Checks that the supplied dictionary matches the JSON Schema
        in another dictionary. If no ``source_dict`` is provided, the
        method will attempt to validate the validation dictionary
        against `attr:self.schema`.

        :param dict dict_to_validate: The dictionary representing the JSON
            against the JSON Schema to be validated
        :param source_dict: The dictionary representing the JSON Schema against
            which the incoming JSON will be compared
        :return: A tuple containing a boolean corresponding to whether the
            schema validated or not, and a message. If the schema validated
            successfully, the message will be ``"success"``. If not, then the
            message will correspond to the reason why the schema did not
            successfully validate
        """
        if source_dict is None:
            source_dict = self.schema

        try:
            jsonschema.validate(dict_to_validate, source_dict)
            return True, 'success'
        except jsonschema.ValidationError as val_error:
            return False, str(val_error)
