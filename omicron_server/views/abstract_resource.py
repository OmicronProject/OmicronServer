import abc
import jsonschema
from functools import wraps
from flask import request, jsonify, abort
from flask.ext.restful import Resource

__author__ = 'Michal Kononenko'


class AbstractResource(Resource):
    """
    Abstract class that defines an API view with a schema
    built into it. This class is capable of serving its schema
    and
    """
    _http_method_list = frozenset([
        'get', 'post', 'put', 'patch', 'delete', 'options', 'head'
    ])

    def validate(self, dict_to_validate, source_dict):
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
        try:
            jsonschema.validate(dict_to_validate, source_dict)
            return True, 'success'
        except jsonschema.ValidationError as val_error:
            return False, str(val_error)

    def options(self):
        """
        Idempotent method that needs to exist simply because Flask maps it
        to an ``OPTIONS`` request directed to this endpoint. The ``OPTIONS``
        endpoint returns headers related to Cross-Origin Resource Sharing (
        CORS), and will eventually return the JSON schema for the endpoint,
        stating what methods are available, as well as an outline for what
        data is returned for the endpoint. Since no actual data is returned,
        the ``OPTIONS`` method does not currently require authentication
        """
        return jsonify({'message': "options_request_success"})


class SchemaDefinedResource(AbstractResource):

    def __init__(self):
        for method in self._http_method_list:
            if hasattr(self, method):
                setattr(self, method, self.show_schema(getattr(self, method)))

    @staticmethod
    def _should_show_schema(string):
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
        @wraps(f)
        def _wrapper(*args, **kwargs):
            if cls._should_show_schema(request.args.get('schema')):
                return jsonify(cls.schema)
            else:
                return f(*args, **kwargs)
        return _wrapper

    @staticmethod
    @abc.abstractproperty
    def schema():
        """
        Return the JSON schema of the view as a dictionary
        """
        raise NotImplementedError

    def validate(self, dict_to_validate, source_dict=None):
        if source_dict is None:
            source_dict = self.schema

        return AbstractResource.validate(
                self, dict_to_validate, source_dict
        )

    def options(self):
        response = jsonify(self.schema)
        return response
