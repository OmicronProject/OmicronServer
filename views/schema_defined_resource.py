import abc
import jsonschema
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
    _http_method_list = frozenset([
        'get', 'post', 'put', 'patch', 'delete', 'options', 'head'
    ])

    def __init__(self):
        for method in self._http_method_list:
            if hasattr(self, method):
                setattr(self, method, self.show_schema(getattr(self, method)))

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
    def show_schema(cls, f, req_to_parse=request):
        show_schema = cls._parse_query_string(req_to_parse.args.get('schema'))

        @wraps(f)
        def _wrapper(*args, **kwargs):
            if show_schema:
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
