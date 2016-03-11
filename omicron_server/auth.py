"""
Contains declarations for HTTP authorization, needed to be put here to avoid a
circular import where :mod:`api_server` imports
:class:`api_views.users.UserContainer`, but
:class:`api_views.users.UserContaner` requires an ``auth`` object
declared in :mod:`api_server`
"""
from uuid import UUID
from flask import g
from flask.ext.httpauth import HTTPBasicAuth
from .config import default_config as conf
from .database import User, Token, ContextManagedSession
import logging

log = logging.getLogger(__name__)

__author__ = 'Michal Kononenko'
auth = HTTPBasicAuth()
database_session = ContextManagedSession(bind=conf.DATABASE_ENGINE)


@auth.verify_password
def verify_password(username_or_token, password=None):
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

    :param str username_or_token: The username or token of the user
        attempting to authenticate into the API
    :param str password: The password or token to be used
        to authenticate into the API. If no password is supplied, this value
        will be ``None``.
    :return: True if the password or token is correct, False if otherwise
    :rtype bool:

    .. _Authorization:
            http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.8
    .. _SSL: https://en.wikipedia.org/wiki/Transport_Layer_Security
    .. _HMAC-SHA256:
            https://en.wikipedia.org/wiki/Hash-based_message_authentication_code
    """
    try:
        UUID(hex=username_or_token)
    except (TypeError, ValueError):
        g.authenticated_from_token = False
        with database_session() as session:
            return _verify_user(username_or_token, password, session)

    with database_session() as session:
        token = session.query(
            Token
        ).filter_by(
            token_hash=Token.hash_token(username_or_token)
        ).first()

        if token is None:
            log.info('Unable to get requested auth token for request %s',
                     g.request_id)
            g.authenticated_from_token = False
            return _verify_user(username_or_token, password, session)

        if token.verify_token(username_or_token):
            g.user = token.owner
            g.authenticated_from_token = True
            return True
        else:
            g.authenticated_from_token = False
            return False


def _verify_user(username, password, session):
    """
    Check if the username matches the user. If it does, write the user
    to :meth:`Flask.g` and return ``True``, else return ``False``
    :param str username: The name of the user to validate
    :param str password: The password to validate
    :param Session session: The database session to use for auth
    :return: ``True`` if the user authenticated and ``False`` if not
    """
    user = session.query(
        User
    ).filter_by(
        username=username
    ).first()

    if user is None:
        log.info('Unable to find user with username %s', username)
        return False

    if user.verify_password(password):
        g.user = user
        return True
