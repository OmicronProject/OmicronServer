"""
Contains the endpoints for the API, created as pluggable objects using
`Flask RESTful<https://flask-restful-cn.readthedocs.org/en/0.3.4/>`_.

"""
from views.schema_defined_resource import SchemaDefinedResource
from views.users import UserContainer, UserView
from views.projects import ProjectContainer

__author__ = 'Michal Kononenko'
