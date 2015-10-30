__author__ = 'Michal Kononenko'
from flask_restful import Resource
from flask import request
import jsonschema
import json

def under_construction():
    return {'status': 'under construction'}


class UserContainer(Resource):
    def __init__(self):
        Resource.__init__(self)

    def get(self):
        return under_construction()

    def post(self):
        jsonschema.validate()