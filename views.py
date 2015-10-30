""" Contains views for the app
"""
from flask import Blueprint

__author__ = 'Michal Kononenko'

views = Blueprint(__name__, 'views')


@views.route('/')
@views.route('/index')
def render_welcome_page():
    """
    Renders the welcome page to the app, will serve the UI
    """
    return 'Hello World'