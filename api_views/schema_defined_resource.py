import abc
import json
from collections import namedtuple
from functools import wraps

import jsonschema
from flask import request, jsonify
from flask.ext.restful import Resource
from werkzeug.exceptions import abort

__author__ = 'Michal Kononenko'


class SchemaDefinedResource(Resource):
    """
    Abstract class that defines an API view with a schema
    built into it. This class is capable of serving its schema
    and
    """
    __metaclass__ = abc.ABCMeta

    __request_params__ = namedtuple(
            'RequestParams', ['show_schema', 'show_data']
    )

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
        pass

    def validate_schema(self, json_to_validate):
        """
        Validate a dictionary representing  schema against :attr:`self.schema`.
        :param dict json_to_validate: The dis
        :return:
        """
        if isinstance(json_to_validate, str):
            json.loads(json_to_validate)
        try:
            jsonschema.validate(json_to_validate, self.schema)
            return True, 'success'
        except jsonschema.ValidationError as val_error:
            return False, str(val_error)