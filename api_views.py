"""
Contains all views for the API
"""
from flask import request, abort, jsonify
from flask_restful import Resource
from json_schema_parser import JsonSchemaValidator
import os
from decorators import restful_pagination
from config import default_config as conf
from db_models import User, sessionmaker

__author__ = 'Michal Kononenko'
database_session = sessionmaker(conf.DATABASE_ENGINE)


class UserContainer(Resource):
    post_schema_validator = JsonSchemaValidator(
        os.path.join(conf.JSON_SCHEMA_PATH, 'users', 'users_post.json')
    )

    def __init__(self):
        Resource.__init__(self)

    @staticmethod
    def parse_search_query_params(request):
        """
        Parse search query parameters
        :return:
        """
        contains = request.args.get('contains')
        if contains is not None:
            return '%%%s%%' % contains
        search_string = ''
        starts_with = request.args.get('starts_with')
        if starts_with is not None:
            search_string = '%s%s' % ('%s%%' % starts_with, search_string)
        ends_with = request.args.get('ends_with')
        if ends_with is not None:
            search_string = '%s%s' % (search_string, '%%%s' % ends_with)

        return search_string

    @restful_pagination()
    def get(self, pag_args):
        like_string = self.parse_search_query_params(request)

        with database_session as session:
            user_query = session.query(
                User
            ).filter(
                User.username.like(like_string)
            ).order_by(
                User.id
            ).limit(
                pag_args.items_per_page
            ).offset(
                pag_args.offset
            )

            users = user_query.all()
            user_count = user_query.count()

        response = jsonify({'users': [user.get for user in users]})
        response.headers['Count'] = user_count
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
