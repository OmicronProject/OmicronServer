"""
Defines the flask app which will run our HTTP application. This also creates
a flask-restful API object, which will serve as the router to the objects in
:mod:`api_views`.
"""
from flask import Flask, g, jsonify
from flask_restful import Api
from flask.ext.httpauth import HTTPBasicAuth
from api_views.users import UserContainer
from db_models import User, sessionmaker
import logging

log = logging.getLogger(__name__)

__author__ = 'Michal Kononenko'

app = Flask(__name__)
api = Api(app, prefix='/api/v1')
auth = HTTPBasicAuth()

api.add_resource(UserContainer, '/users', endpoint='users')


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


@auth.verify_password
def verify_password(username_or_token, password):
    """
    Callback function for
    :func:`flask.ext.httpauth.HTTPBasicAuth.verify_password`, used
    to verify both username and password authentication, as well as
    authentication tokens.

    In order to authenticate, the user must use base64 encoding, encode a
    string of the form ``username:password``, and submit the encoded string
    in the request's Authorization_. header.

    Alternatively, the user can encode their token in base64, and submit this
    in their Authorization_. header. In this case, the incoming password
    will be ``None``.

    .. warning::

        Basic Authentication, unless done over SSL_. **IS NOT A SECURE FORM**
        ** OF AUTHENTICATION**, as **ANYONE** can intercept an HTTP request,
        and decode the information in the Authorization header. This will be
        solved in two ways

        - Any production deployment of this API will be done using SSL
        - HMAC-SHA256_. authentication will be supported, although this is
            currently out of scope for the Christmas Release of this API

    :param str username_or_token: The username or the token of the user
        attempting to authenticate into the API
    :param str password: The password supplied by the user in his attempt to
        authenticate
    :return: True if the password or token is correct, False if otherwise
    :rtype bool:

    .. _Authorization http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#
        sec14.8
    .. _SSL https://en.wikipedia.org/wiki/Transport_Layer_Security
    .. _HMAC-SHA256 https://en.wikipedia.org/wiki/Hash-based_message_authentication_code
    """
    user = User.verify_auth_token(username_or_token)
    if user:
        g.user = user
        return True

    with sessionmaker() as session:
        user = session.query(
            User
        ).filter_by(
            username=username_or_token
        ).first()

    if not user:
        return False
    elif user.verify_password(password):
        return True
    else:
        return False
