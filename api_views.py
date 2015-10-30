__author__ = 'Michal Kononenko'
from flask import request, abort
from flask_restful import Resource
from json_schema_parser import JsonSchemaValidator
import os
from config import JSON_SCHEMA_PATH
from db_models import User, sessionmaker

def under_construction():
    return {'status': 'under construction'}


class UserContainer(Resource):
    post_schema_validator = JsonSchemaValidator(
        os.path.join(JSON_SCHEMA_PATH, 'users_post.json')
    )
    
    def __init__(self):
        Resource.__init__(self)

    def get(self):
        return under_construction()

    def post(self):
        if not self.post_schema_validator.validate_dict(request.json):
            abort(400)

        user = User(
            username=request.json.get('user'),
            password=request.json.get('password'),
            email=request.json.get('email')
        )

        session = sessionmaker()

        try:
            session.add(user)
            session.commit()
        except:
            session.rollback()
            raise

