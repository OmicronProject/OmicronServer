"""
Runs the API
"""
from flask import Flask
from views import views

__author__ = 'Michal Kononenko'

app = Flask(__name__)

app.register_blueprint(views)
