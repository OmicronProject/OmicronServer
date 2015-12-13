"""
Contains the endpoints for the API, created as pluggable objects using
`Flask RESTful<https://flask-restful-cn.readthedocs.org/en/0.3.4/>`_.

"""

__author__ = 'Michal Kononenko'


class BadSchemaError(Exception):
    pass
