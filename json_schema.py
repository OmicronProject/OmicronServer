"""
Contains an abstract representation of a REST API view, as well as a
subclass of Marshmallow
"""
from marshmallow import fields, Schema, ValidationError

__author__ = 'Michal Kononenko'


class RequiredFieldNotFoundError(Exception):
    """
    Thrown if a field that is not required is listed as a required field
    """
    pass


class MarshmallowJSONSchema(Schema):
    """
    Exposes the JSON Schema for a given schema
    """
    required = ()
    meta_schema = "http://json-schema.org/draft-04/schema#"
    title = None
    description = None
    type = 'object'

    def __init__(self, strict=True, **kwargs):
        super(Schema, self).__init__(strict=strict, **kwargs)

    def _check_required_fields_in_schema(self):
        for field in self.required:
            if field not in self.__dict__.keys():
                raise RequiredFieldNotFoundError(
                        'Unable to find field %s in schema %s',
                        field, self.__repr__()
                )

    @property
    def schema(self):
        schema = {"$schema": self.meta_schema, 'type': self.type}
        if self.title is not None:
            schema['title'] = self.title
        if self.description is not None:
            schema['description'] = self.description
        return schema

    def __repr__(self):
        return '%s(title=%s, description=%s)' % (
            self.__class__.__name__, self.title, self.description
        )


class DateTime(fields.DateTime):
    """
    """
    type = 'date'

    def __init__(self, description=None, **kwargs):
        super(DateTime, self).__init__(**kwargs)
        self.description = description

    @property
    def schema(self):
        schema = dict(type=self.type)
        if self.description is not None:
            schema['description'] = self.description
        return schema


class Integer(fields.Integer):
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
        schema = dict()
        if self.description is not None:
            schema['description'] = self.description
        if self.minimum is not None:
            schema['minimum'] = self.minimum
        if self.maximum is not None:
            schema['maximum'] = self.maximum

        return schema
