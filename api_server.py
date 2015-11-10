"""
Defines the flask app which will run our HTTP application. This also creates
a flask-restful API object, which will serve as the router to the objects in
:mod:`api_views`.
"""
from flask import Flask, g, jsonify
from flask_restful import Api
from flask.ext.httpauth import HTTPBasicAuth
from api_views.users import UserContainer
from db_models import User
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
    Base URL to confirm that the API actually works
    :return:
    """
    return 'Hello World!'


@app.route('/api/v1/token')
@auth.login_required
def get_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


@auth.verify_password
def verify_password(username_or_token, password):
    user = User.verify_auth_token(username_or_token)
    if not user:
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True
