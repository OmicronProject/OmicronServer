"""
Contains unit tests for :mod:`decorators`
"""
import unittest
import decorators
import json
from api_server import app
from flask import jsonify

__author__ = 'Michal Kononenko'
url = '/test_pagination'


@app.route(url)
@decorators.restful_pagination()
def _get_pagination_arguments(pag_args):
    """
    Dynamically inject the URL into the app, so that pagination should be
    tested. The endpoint simply returns the pagination arguments
    in JSON

    **Example Request**

    .. sourcecode:: http

        HTTP/1.1 GET /test_pagination?page=1&items_per_page=10
        Content-type: application/json

    **Example Response**

    .. sourcecode:: http

        HTTP/1.1 GET 200 OK

        {
            "page": 1,
            "items_per_page": 1000
        }

    :param PaginationArgs pag_args: A named tuple of pagination arguments
        dynamically injected into the endpoint
    :return:
    """

    return jsonify(
        {'page': pag_args.page,
         'items_per_page': pag_args.items_per_page
         }
    )


class TestRestfulPagination(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client(True)
        self.headers = {'content-type': 'application/json'}
        self.url = url
        self.request_method = self.client.get

    def test_restful_pagination(self):
        page = 1
        items_per_page = 100

        test_url = '%s?page=%d&items_per_page=%d' % (self.url, page, items_per_page)

        r = self.request_method(test_url, headers=self.headers)

        self.assertEqual(r.status_code, 200)

        response_dict = json.loads(r.data.decode('utf-8'))

        self.assertEqual(response_dict['page'], page)
        self.assertEqual(response_dict['items_per_page'], items_per_page)

    def test_default_page_is_1(self):
        items_per_page = 100

        test_url = '%s?items_per_page=%d' % (self.url, items_per_page)

        r = self.request_method(test_url, headers=self.headers)
        self.assertEqual(r.status_code, 200)

        response_dict = json.loads(r.data.decode('utf-8'))

        self.assertEqual(response_dict['page'], 1)

    def test_page_string_argument(self):
        items_per_page = 100
        page = 'foo'

        test_url = '%s?page=%s&items_per_page=%d' % (self.url, page, items_per_page)

        r = self.request_method(test_url, headers=self.headers)

        self.assertEqual(r.status_code, 200)

        response_dict = json.loads(r.data.decode('utf-8'))

        self.assertEqual(response_dict['page'], 1)

    def test_items_per_page_default_arg(self):
        page = 1
        test_url = '%s?page=%d' % (self.url, page)

        r = self.request_method(test_url, headers=self.headers)

        self.assertEqual(r.status_code, 200)

        response_dict = json.loads(r.data.decode('utf-8'))

        self.assertEqual(response_dict['items_per_page'], 1000)

    def test_items_per_page_string_arg(self):
        page = 1
        items_per_page = 'foo'

        test_url = '%s?page=%d&items_per_page=%s' % \
                   (self.url, page, items_per_page)

        r = self.request_method(test_url, headers=self.headers)

        self.assertEqual(r.status_code, 200)

        response_dict = json.loads(r.data.decode('utf-8'))

        self.assertEqual(response_dict['items_per_page'], 1000)

    def test_function_name_preservation(self):
        """
        Result of a bug that occurred with the decorator, in that the wrapped
        function was not passing the name and docstring of ``f``. This resulted
        in Sphinx being unable to write the docstring of the wrapped function
        """
        def _function_to_decorate():
            raise NotImplementedError

        function_name = _function_to_decorate.__name__
        function_doc = _function_to_decorate.__doc__

        decorated_function = \
            decorators.restful_pagination()(_function_to_decorate)

        self.assertEqual(decorated_function.__name__, function_name)
        self.assertEqual(decorated_function.__doc__, function_doc)

    def test_function_name_carrying_with_decorator(self):
        function_docstring = 'foo'

        @decorators.restful_pagination()
        def _function_to_decorate():
            raise NotImplementedError

        _function_to_decorate.__doc__ = function_docstring

        self.assertNotEqual(
            decorators.restful_pagination().__name__,
            _function_to_decorate.__name__
        )

        self.assertEqual(function_docstring, _function_to_decorate.__doc__)