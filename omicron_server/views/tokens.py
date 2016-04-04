"""
Contains endpoints for working with authentication tokens.
"""
from ..views import AbstractResource
from ..config import default_config as conf
from ..database import ContextManagedSession
from ..models import Token, Administrator
from ..auth import auth
from flask import g, jsonify, request

__author__ = 'Michal Kononenko'

database_session = ContextManagedSession(bind=conf.DATABASE_ENGINE)


class Tokens(AbstractResource):
    """
    Maps the ``/tokens`` endpoint. Users can ``POST`` to this endpoint to
    create authentication tokens, or they can send a ``DELETE`` request to
    delete their tokens.
    """
    class TokenProcessingError(Exception):
        """
        Thrown if there is an issue processing the body of a ``DELETE``
        request. This lets the endpoint know that a 400 error needs to be
        returned instead of continuing execution along the happy path.
        """
        pass

    @database_session()
    @auth.login_required
    def post(self, session):
        """
        Use the user's ``username:password`` credentials, and create a new
        authentication token. The auth token is a UUID-1. The expiration time
        is set by passing in the number of seconds from now that the token
        is good for, as a query parameter. The default token expiration time is
        determined in the variable
            :attr:`omicron_server.config.Config.DEFAULT_TOKEN_EXPIRATION_TIME`

        **Example Request**

        .. sourcecode:: http

            POST /tokens HTTP/1.1

        **Example Response**

        .. sourcecode:: http

            HTTP/1.1 201 CREATED
            Content-Type: application/json

            {
                "token": "445ee3d0-f503-11e5-9ce9-5e5517507c66",
                "expiration_date": "2016-03-28T17:05:46.396928"
            }

        :query expiration: An integer representing the number of seconds
            for which the token will be active. The default is given by the
            variable
            :attr:`omicron_server.config.Config.DEFAULT_TOKEN_EXPIRATION_TIME`
        :statuscode 201: No error, the token was created successfully
        :statuscode 400: A bad request was made to the server
        :statuscode 403: An attempt was made to create a token with an existing
            token. This is forbidden

        :param ContextManagedSession session: The database session that will be
            used for communicating with the database
        :return: The relevant Flask response
        :rtype: flask.Response
        """
        if g.authenticated_from_token:
            return self._authenticated_from_token_response

        try:
            expiration_time = int(request.args.get('expiration'))
        except TypeError:
            expiration_time = conf.DEFAULT_TOKEN_EXPIRATION_TIME

        token, expiration_date = g.user.generate_auth_token(
            expiration=expiration_time, session=session
        )

        return self._successful_response(token, expiration_date)

    @database_session()
    @auth.login_required
    def delete(self, session):
        """
        Delete a token for the user. If no request body is provided,
        the token to be deleted will be token that is currently being used
        to log in. If the user authenticates with their
        ``username:password`` credentials, they will need to provide the
        token that they want to delete in the request body.

        **Example Request**

        .. sourcecode:: http

            DELETE /tokens HTTP/1.1
            Content-Type: application/json
            Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=

            {
                "token": "2eb51102-f509-11e5-9ce9-5e5517507c66"
            }

        **Example Response**

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
                "token_status": "deleted"
            }

        :statuscode 200: The token was deleted successfully
        :statuscode 400: The endpoint was unable to delete the token

        :param ContextManagedSession session: The database session that will be
            used for communicating with the database
        :return: The relevant Flask response
        :rtype: flask.Response
        """
        try:
            token_string = self.get_token_string(request)
        except self.TokenProcessingError as error:
            return self.make_400_error_response(error)
        token_query = session.query(Token).filter_by(
            token_hash=Token.hash_token(token_string)
        )

        if isinstance(g.user, Administrator):
            token = token_query.first()
        else:
            token = token_query.filter(Token.owner == g.user).first()

        if token is None:
            return self.make_400_error_response(
                'Unable to find the requested token'
            )

        with session() as session:
            token.revoke(session)

        response = jsonify({'token_status': 'deleted'})
        return response

    @staticmethod
    def _successful_response(token, expiration_date):
        """
        Returns a template response with the appropriate status code for token
        creation. When a user ``POST``s to the endpoint, and execution
        follows the happy path, the user will get this at the end

        :param str token: The raw token that the user can use to substitute
            their login credentials
        :param str expiration_date: An ISO-8601 date string representing the
            expiration date of the token
        :return: A flask response containing the two parameters above and
            the correct status code
        """
        response = jsonify({
            "token": token,
            "expiration_date": expiration_date.isoformat()
        })
        response.status_code = 201
        return response

    @property
    def _authenticated_from_token_response(self):
        """
        If the user attempted to create a new token with an existing token,
        this response is returned

        :return: The appropriate flask Response
        """
        response = jsonify({'error': 'attempted to create new token with '
                                     'existing token'})
        response.status_code = 403
        return response

    def get_token_string(self, req_to_parse):
        """
        Parse the request to get the token that should be deleted. If the
        user authenticated from a token, use that token. If the user did not,
        return the token from the request body.

        :param flask.request req_to_parse: The request from which the token
            string is to be retrieved
        :return: The token to be deleted
        :rtype: str
        :raises:
            :class:`omicron_server.views.tokens.Tokens.TokenProcessingError`
            if unable to retrieve the token string from the user's
            credentials or from the request body.
        """
        if g.authenticated_from_token:
            token_string = g.token_string
        else:
            if req_to_parse.json is None:
                raise self.TokenProcessingError(
                    'Unable to parse JSON'
                )
            try:
                token_string = req_to_parse.json['token']
            except KeyError:
                raise self.TokenProcessingError(
                    'The "token" key was not found in the supplied JSON'
                )

        return token_string

    @staticmethod
    def make_400_error_response(message):
        """
        Return a generic 400 error response with the required message

        :param str message: The message to display
        :return: A flask response with the message in the body and a 400
            status code
        """
        response = jsonify({'error': message})
        response.status_code = 400
        return response
