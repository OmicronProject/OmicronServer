"""
Contains utilities for loading, parsing, and validating inputs against
a JSON schema
"""
import json
import jsonschema
import logging
import os
__author__ = 'Michal Kononenko'

log = logging.getLogger(__name__)


class FileNotFoundError(ValueError):
    """
    Thrown if the parser is unable to find the file
    """
    pass


class BadJsonSchemaError(Exception):
    """
    Thrown if the JSON Schema presented is not a valid draft 3 or draft 4
    schema
    """
    pass


class JsonSchemaValidator(object):
    """
    Contains utilities for validating JSONSchema from a file
    """
    def __init__(self, path):
        """
        Initialize the schema
        :param path: the path from which the file should be pulled
        :param schema_dict:
        """
        if not os.path.isfile(path):
            raise FileNotFoundError('Unable to find file with path <%s>',
                                    path)
        else:
            self.json_dict = self._read_schema_from_file(path)
        format_checker = jsonschema.FormatChecker()
        is_draft_3 = format_checker.conforms(self.json_dict, 'draft3')
        is_draft_4 = format_checker.conforms(self.json_dict, 'draft4')

        if not (is_draft_3 or is_draft_4):
            raise BadJsonSchemaError(
                'schema dict %s does not correspond to a draft 3 or draft '
                '4 JSON Schema', self.json_dict)

        self.path = path

    @staticmethod
    def _read_schema_from_file(path):
        """
        Read the file containing the JSON Schema and return it as a
        json-loaded dictionary
        :return:
        """
        with open(path, mode='r') as json_file:
            file_string = ''.join([line for line in json_file])
        return json.loads(file_string)

    def validate_dict(self, dict_to_validate):
        """
        Validates a dictionary against :attr:`self.json_dict`.
        :param dict dict_to_validate: The dictionary to check against
        :attr:`self.json_dict`, representing the base JSON Schema to validate.

        :return: True if the dictionary is allowed by the schema and false if
            not.
        """
        if dict_to_validate is not None:
            try:
                jsonschema.validate(dict_to_validate, self.json_dict)
                return True
            except jsonschema.ValidationError:
                return False
            except jsonschema.SchemaError:
                log.error('The schema at path %s is not valid', self.path)
        else:
            return False
