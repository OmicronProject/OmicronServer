"""
Defines the flask app which will run our HTTP application. This also creates
a flask-restful API object, which will serve as the router to the objects in
:mod:`api_views`.
"""
import logging

from omicron_server.auth import auth
from omicron_server.database import Administrator, User, ContextManagedSession
from flask import Flask, g, jsonify, request, abort
from flask.ext.cors import CORS
from flask_restful import Api
from omicron_server.config import default_config as conf
from omicron_server.views import UserContainer, UserView, ProjectContainer
from omicron_server.views import Projects
from omicron_server.decorators import crossdomain

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

__author__ = 'Michal Kononenko'

app = Flask(__name__)
api = Api(app, prefix='/api/v1')

api.add_resource(UserContainer, '/users')
api.add_resource(UserView, '/users/<username_or_id>')
api.add_resource(ProjectContainer, '/projects')
api.add_resource(Projects, 'projects/<project_name_or_id>')

database_session = ContextManagedSession(bind=conf.DATABASE_ENGINE)


@app.route('/', methods=["GET", "OPTIONS"])
@app.route('/index', methods=["GET", "OPTIONS"])
@crossdomain(origin='*')
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
    return jsonify({'message': 'hello_world'})


@app.route('/api/v1/token', methods=['POST'])
@crossdomain(origin='*')
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
            "token": "a409a362-d733-11e5-b625-7e14f79230d0",
            "expiration_date": "2015-01-01T12:00:00"
        }

    :return: A Flask response object with the token jsonified into ASCII
    """
    try:
        token, expiration_date = g.user.generate_auth_token(
            expiration=int(request.args.get('expiration'))
        )
    except TypeError:
        log.debug('No expiration supplied, using default expiration time')
        token, expiration_date = g.user.generate_auth_token()
    response = jsonify(
            {'token': token,
             'expiration_date': expiration_date.isoformat()
        }
    )
    response.status_code = 201
    return response


@app.route('/api/v1/token', methods=['DELETE'])
@crossdomain(origin='*')
@auth.login_required
def revoke_token():
    """
    Revoke the current token for the user that has just authenticated,
    or the user with username given by a query parameter, allowed only if the
    user is an Administrator
    """
    username_to_delete = request.args.get('username')
    if username_to_delete is None:
        username_to_delete = g.user.username
    else:
        username_to_delete = str(username_to_delete)

    if isinstance(g.user, Administrator):
        with database_session() as session:
            user = session.query(
                User
            ).filter_by(
                username=username_to_delete
            ).first()
            if user is None:
                abort(404)
            user.current_token.first().revoke()
    else:
        with database_session() as session:
            session.query(g.user.__class__).filter_by(
                id=g.user.id
            ).first().current_token.first().revoke()

    response = jsonify({'token_status': 'deleted'})
    return response
