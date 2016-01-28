"""
Contains methods for displaying, creating, and validating JSON
Schemas
"""
import json_schema.fields as fields

__author__ = 'Michal Kononenko'


class RequiredFieldNotFoundError(Exception):
    """
    Thrown if a field that is not required is listed as a required field
    """
    pass
