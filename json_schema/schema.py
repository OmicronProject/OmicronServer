"""
Contains a base class for exposing a Marshmallow schema with a JSON schema
representation
"""
from marshmallow.schema import Schema

__author__ = 'Michal Kononenko'


class MarshmallowJSONSchema(Schema):
    """
    Exposes the JSON Schema for a given schema
    """
    meta_schema = "http://json-schema.org/draft-04/schema#"
    title = None
    description = None
    type = 'object'

    def __init__(self, strict=True, **kwargs):
        Schema.__init__(self, strict=strict, **kwargs)

    @property
    def required_fields(self):
        return [field_name for field_name in self.fields
                if self.fields[field_name].required]

    @property
    def schema(self):
        schema = {"$schema": self.meta_schema, 'type': self.type}
        if self.title is not None:
            schema['title'] = self.title
        if self.description is not None:
            schema['description'] = self.description

        schema['properties'] = {
            field: self.fields[field].schema for field in self.fields if
            hasattr(self.fields[field], 'schema')}

        schema['required'] = self.required_fields

        return schema

    def __repr__(self):
        return '%s(title=%s, description=%s)' % (
            self.__class__.__name__, self.title, self.description
        )
