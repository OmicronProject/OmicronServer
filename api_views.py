"""
Contains all views for the API
"""
from flask import request, abort, jsonify
from flask_restful import Resource
from json_schema_parser import JsonSchemaValidator
import os
from config import JSON_SCHEMA_PATH, DATABASE_ENGINE
from db_models import User, sessionmaker

__author__ = 'Michal Kononenko'
database_session = sessionmaker(DATABASE_ENGINE)


def under_construction():
    return jsonify({'status': 'under construction'}), 200


class UserContainer(Resource):
    post_schema_validator = JsonSchemaValidator(
        os.path.join(JSON_SCHEMA_PATH, 'users_post.json')
    )

    def __init__(self):
        Resource.__init__(self)

    def get(self):
        with database_session as session:
            users = session.query(User).all()

        response = jsonify({'users': [user.get for user in users]})
        return response

    def post(self):
        if not self.post_schema_validator.validate_dict(request.json)[0]:
            abort(400)

        username = request.json.get('username')
        password = request.json.get('password')
        email = request.json.get('email')

        user = User(username, password, email)
        with database_session as session:
            session.add(user)

        response = jsonify({'user': username, 'email': email})
        response.status_code = 201

        return response
