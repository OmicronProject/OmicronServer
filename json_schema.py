"""
Contains an abstract representation of a REST API view, as well as a
subclass of Marshmallow
"""
from marshmallow import fields, Schema, ValidationError
import re

__author__ = 'Michal Kononenko'