"""
Defines the flask app which will run our HTTP application. This also creates
a flask-restful API object, which will serve as the router to the objects in
:mod:`api_views`.
"""
import logging
from flask import Flask, g, jsonify
from flask_restful import Api
from uuid import uuid1
from .config import default_config as conf
from .database import ContextManagedSession
from .decorators import crossdomain
from .views import UserContainer, UserView, ProjectContainer
from .views import Projects
from .views import Tokens

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

__author__ = 'Michal Kononenko'

app = Flask(__name__)
api = Api(app, decorators=[crossdomain(origin='*')])

api.add_resource(UserContainer, '/users')
api.add_resource(UserView, '/users/<username_or_id>')
api.add_resource(ProjectContainer, '/projects')
api.add_resource(Projects, '/projects/<project_name_or_id>')
api.add_resource(Tokens, '/tokens')

database_session = ContextManagedSession(bind=conf.DATABASE_ENGINE)


@app.before_request
@database_session()
def setup_request(session):
    g.request_id = str(uuid1())
    g.session = session


@app.after_request
def teardown_request(response):
    g.session.close()

    response.headers['Request-Id'] = g.request_id
    return response


@app.route('/', methods=["GET", "OPTIONS"])
@app.route('/index', methods=["GET", "OPTIONS"])
@crossdomain(origin='*')
def hello_world():
    """
    Base URL to confirm that the API actually works.
    Serves a few relevant URLs and info related to the API.

    **Example Response**

    .. sourcecode:: http

        GET / HTTP/1.1
        Content-Type: application/json

        {
            'meta': {
                'source_repository': 'https://github.com/MichalKononenko \
                /OmicronServer'
            }
        }

    .. _OmicronClient: https://github.com/MichalKononenko/OmicronClient

    :return: Hello, world!
    :rtype: str
    """
    return jsonify(
        {
            'meta': {
                'source_repository':
                    'https://github.com/MichalKononenko/OmicronServer',
                'issue_tracking':
                    'https://waffle.io/MichalKononenko/OmicronServer',
                'documentation':
                    'https://omicron-server.readthedocs.org/en/latest/',
                'dependency_management':
                    'https://requires.io/github/MichalKononenko/OmicronServer'
                    '/requirements/?branch=master',
                'maintainer': {
                    'name': "Michal Kononenko",
                    'email': 'mkononen@uwaterloo.ca'
                },
                'version': '0.1'
            }
        }
    )
