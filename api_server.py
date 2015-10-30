"""
Runs the API
"""
from flask import Flask
from flask_restful import Api
import api_views

__author__ = 'Michal Kononenko'

app = Flask(__name__)
api = Api(app, prefix='/api/v1')


api.add_resource(api_views.UserContainer, '/users', endpoint='users')


@app.route('/')
@app.route('/index')
def hello_world():
    """
    Base URL to confirm that the API actually works
    :return:
    """
    return 'Hello World!'