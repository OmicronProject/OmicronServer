"""
Contains the endpoints for the API, created as pluggable objects using
`Flask RESTful<https://flask-restful-cn.readthedocs.org/en/0.3.4/>`_.

"""
from .schema_defined_resource import SchemaDefinedResource
from .projects import Projects, ProjectContainer
from .users import UserContainer, UserView
__author__ = 'Michal Kononenko'
