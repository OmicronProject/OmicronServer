"""
Extends Marshmallow's marshalling features by providing
data types
"""
from marshmallow import ValidationError
from marshmallow import fields as _marshmallow_fields
import re
__author__ = 'Michal Kononenko'


class DateTime(_marshmallow_fields.DateTime):
    """
    """
    type = 'datetime'

    def __init__(self, description=None, **kwargs):
        super(DateTime, self).__init__(**kwargs)
        self.description = description

    @property
    def schema(self):
        schema = dict(type=self.type)
        if self.description is not None:
            schema['description'] = self.description
        return schema


class Integer(_marshmallow_fields.Integer):
    """
    Overwrites the Integer field and includes its JSON schema
    """
    type = 'integer'

    def __init__(
            self, description=None, as_string=False, minimum=None,
            maximum=None, **kwargs
    ):
        super(Integer, self).__init__(as_string, **kwargs)
        self.description = description
        self.minimum = minimum
        self.maximum = maximum
        self.validators.append(self._validate_quantity)

    def _validate_quantity(self, value):
        if self.minimum is not None:
            if value < self.minimum:
                raise ValidationError(
                    'The value %d is less than the minimum allowed '
                    'value of %d in field %s',
                    value, self.minimum, self.__repr__()
                )
        if self.maximum is not None:
            if value > self.maximum:
                raise ValidationError(
                    'The value %d is greater than the maximum allowed value '
                    'of %d in field %s',
                    value, self.maximum, self.__repr__()
                )

        super(Integer, self)._validate(value)

    @property
    def schema(self):
        schema = dict(type=self.type)
        if self.description is not None:
            schema['description'] = self.description
        if self.minimum is not None:
            schema['exclusiveMinimum'] = self.minimum
        if self.maximum is not None:
            schema['exclusiveMaximum'] = self.maximum

        return schema


class String(_marshmallow_fields.String):
    """
    Contains a JSON Schema-compliant datatype for string
    """
    type = 'string'

    def __init__(
            self, description=None, regex_pattern=None, *args, **kwargs
    ):
        super(String, self).__init__(*args, **kwargs)
        self.description = description

        if regex_pattern is not None:
            self.regex = re.compile(regex_pattern)
            self.validators.append(self._validate_against_regex)
        else:
            self.regex = None

    def _validate_against_regex(self, value):
        return self.regex.search(value) is not None


class Nested(_marshmallow_fields.Nested):
    description = None
    type = 'object'

    def __init__(self, *args, strict=True, **kwargs):
        _marshmallow_fields.Nested.__init__(self, *args, **kwargs)
        self.strict = strict

    @property
    def schema(self):
        schema = dict(type=self.type)
        if self.description is not None:
            schema['description'] = self.description

        return schema


class List(_marshmallow_fields.List):
    def __init__(self, *args, strict=True, **kwargs):
        _marshmallow_fields.List.__init__(self, *args, strict=strict, **kwargs)
