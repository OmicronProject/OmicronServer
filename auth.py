"""
Contains declarations for HTTP authorization, needed to be put here to avoid a
circular import where :mod:`api_server` imports
:class:`api_views.users.UserContainer`, but
:class:`api_views.users.UserContaner` requires an ``auth`` object
declared in :mod:`api_server`
"""
from flask import g
from flask.ext.httpauth import HTTPBasicAuth
from config import default_config as conf
from db_models.db_sessions import ContextManagedSession
from db_models.users import User

__author__ = 'Michal Kononenko'
auth = HTTPBasicAuth()
database_session = ContextManagedSession(bind=conf.DATABASE_ENGINE)


@auth.verify_password
def verify_password(username, password_or_token):
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

    :param str username: The username of the user
        attempting to authenticate into the API
    :param str password_or_token: The password or token to be used
        to authenticate into the API.
    :return: True if the password or token is correct, False if otherwise
    :rtype bool:

    .. _Authorization: http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.8
    .. _SSL: https://en.wikipedia.org/wiki/Transport_Layer_Security
    .. _HMAC-SHA256: https://en.wikipedia.org/wiki/Hash-based_message_authentication_code
    """
    with database_session() as session:
        user = session.query(
            User
        ).filter_by(
            username=username
        ).first()

    if not user:
        return False

    if (user.verify_password(password_or_token) or
            user.verify_auth_token(password_or_token)):
        g.user = user
        return True
    else:
        return False
