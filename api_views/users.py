"""
Contains views for the ``/users`` endpoint.
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
    """
    Maps the /users endpoint's ``GET`` and ``POST`` requests, allowing API
    consumers to create new users
    """
    post_schema_validator = JsonSchemaValidator(
        os.path.join(conf.JSON_SCHEMA_PATH, 'users', 'users_post.json')
    )

    def __init__(self):
        Resource.__init__(self)

    @staticmethod
    def parse_search_query_params(request):
        """
        This method enables text search over the results returned by a
        ``GET`` request on the ``/users`` endpoint. It parses query parameters
        from :class:`Flask.request`, a container for the HTTP request sent into
        the method. Currently, the query parameters parsed here are

         - starts_with: A string stating what the username should begin with
         - contains: A string specifiying what the username should contain
         - ends_with: A string stating what the username should end with

        :param request: The flask request from which query parameters need to
            be retrieved
        :return: A ``%`` delineated search string ready for insertion as a
            parameter into a SQL or SQLAlchemy query language's ``LIKE`` clause
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
        """
        Process a GET request for the /users endpoint

        **Example request**

        .. sourcecode:: http

            GET /api/v1/users HTTP/1.1
            Host: example.com
            Content-Type: application/json

        **Example response**

        .. sourcecode:: http

            Vary: Accept
            Content-Type: application/json

            .. include:: /schemas/users/examples/get.json

        :query contains: A string specifying what substring should be contained
            in the username. Default is ``''``
        :query starts_with: The substring that the username should start with.
            Default is ``''``.
        :query page: The number of the page to be displayed. Defaults to ``1``.
        :query items_per_page: The number of items to be displayed on this page
            of the results. Default is ``1000`` items.

        :statuscode 200: no error

        :param PaginationArgs pag_args: The pagination arguments generated by
            the ``@restful_pagination()`` decorator, injected into the function
            at runtime
        :return: A flask response object with the search request parsed
        """
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
