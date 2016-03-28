"""
Contains endpoints for working with authentication tokens
"""
from ..views import AbstractResource
from ..config import default_config as conf
from ..database import ContextManagedSession, Token, Administrator
from ..auth import auth
from flask import g, jsonify, request

__author__ = 'Michal Kononenko'

database_session = ContextManagedSession(bind=conf.DATABASE_ENGINE)


class RequestParseError(Exception):
    pass


class Tokens(AbstractResource):

    class TokenProcessingError(Exception):
        pass

    @database_session()
    @auth.login_required
    def post(self, session):
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

        token.revoke()
        response = jsonify({'token_status': 'deleted'})

        return response

    @staticmethod
    def _successful_response(token, expiration_date):
        response = jsonify({
            "token": token,
            "expiration_date": expiration_date.isoformat()
        })
        response.status_code = 201
        return response

    @property
    def _authenticated_from_token_response(self):
        response = jsonify({'error': 'attempted to create new token with '
                                     'existing token'})
        response.status_code = 403
        return response

    def get_token_string(self, req_to_parse):
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
        response = jsonify({'error': message})
        response.status_code = 400
        return response
