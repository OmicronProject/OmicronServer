"""
Defines the flask app which will run our HTTP application. This also creates
a flask-restful API object, which will serve as the router to the objects in
:mod:`api_views`.
"""
from flask import Flask, g, jsonify
from flask_restful import Api
from api_views.users import UserContainer, UserView
import logging
from auth import auth

log = logging.getLogger(__name__)

__author__ = 'Michal Kononenko'

app = Flask(__name__)
api = Api(app, prefix='/api/v1')

api.add_resource(UserContainer, '/users')
api.add_resource(UserView, '/users/<username>')


@app.route('/')
@app.route('/index')
def hello_world():
    """
    Base URL to confirm that the API actually works. Eventually, this endpoint
    will serve the OmicronClient_. JavaScript UI to users.

    **Example Response**

    .. sourcecode:: http

        GET / HTTP/1.1
        Content-Type: application/json

        Hello World!

    .. _OmicronClient: https://github.com/MichalKononenko/OmicronClient

    :return: Hello, world!
    :rtype: str
    """
    return 'Hello World!'


@app.route('/api/v1/token', methods=['POST'])
@auth.login_required
def create_token():
    """
    Generate a user's auth token from the user in Flask's :attr:`Flask.g`
    object, which acts as an object repository unique to each request. Expects
    an Authorization header with Basic Auth.

    **Example Request**

    .. sourcecode:: http

        POST /api/v1/token HTTP/1.1
        Host: example.com
        Content-Type: application/json
        Authorization: B12kS1l2jS1=

    **Example Response**

    .. sourcecode:: http

        Content-Type: application/json

        {
            "token": "1294DKJFKAJ9224ALSJDL1J23"
        }

    :return: A Flask response object with the token jsonified into ASCII
    """
    token = g.user.generate_auth_token()
    response = jsonify({'token': token.decode('ascii')})
    response.status_code = 201
    return response
