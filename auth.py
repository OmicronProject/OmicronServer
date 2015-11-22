"""
Contains declarations for HTTP authorization, needed to be put here to avoid a
circular import where :mod:`api_server` imports
:class:`api_views.users.UserContainer`, but
:class:`api_views.users.UserContaner` requires an ``auth`` object
declared in :mod:`api_server`
"""
from flask.ext.httpauth import HTTPBasicAuth

__author__ = 'Michal Kononenko'
auth = HTTPBasicAuth()
