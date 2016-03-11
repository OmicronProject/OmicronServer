import json
import unittest
import mock
from omicron_server import app
from flask import jsonify
from omicron_server import decorators
from datetime import timedelta

__author__ = 'Michal Kononenko'
url = '/test_pagination'


@app.route(url)
@decorators.restful_pagination()
def _get_pagination_arguments(pag_args):

    return jsonify(
        {'page': pag_args.page,
         'items_per_page': pag_args.items_per_page,
         'offset': pag_args.offset
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

    def test_items_per_page_default_offset(self):
        """
        Tests that `issue #124`_ is resolved, and that the default offset value
        is 0 for any records. This will return the first set of records.

        .. _issue #124: https://goo.gl/hBqXNs
        """
        r = self.request_method(self.url, headers=self.headers)
        self.assertEqual(r.status_code, 200)

        response_dict = json.loads(r.data.decode('utf-8'))
        self.assertEqual(response_dict['offset'], 0)

    def test_negative_items_per_page_error_handling(self):
        items_per_page = -10
        test_url = '%s?items_per_page=%d' % (
            self.url, items_per_page
        )

        r = self.request_method(test_url, headers=self.headers)
        self.assertEqual(r.status_code, 400)

    def test_negative_page(self):
        page = -10
        test_url = '%s?page=%d' % (self.url, page)

        r = self.request_method(test_url, headers=self.headers)
        self.assertEqual(r.status_code, 400)

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


class TestCrossdomainDecorator(unittest.TestCase):
    def setUp(self):
        self.origin = '*'
        self.methods = ["HEAD", "GET", "OPTIONS"]
        self.headers = {"content-type", "authorization"}
        self.default_max_age = 21600

        self.context = app.test_request_context('/index')
        self.context.push()

    def tearDown(self):
        self.context.pop()

    def _compare_headers(self, response, expected_origin, expected_methods,
                         expected_max_age):
        self.assertEqual(
            expected_origin,
            response.headers['Access-Control-Allow-Origin']
        )
        self.assertEqual(
            set(expected_methods),
            set(response.headers["Access-Control-Allow-Methods"].split(', '))
        )
        self.assertEqual(
            str(expected_max_age),
            response.headers["Access-Control-Max-Age"]
        )

    def test_decorator_default_args(self):
        response = decorators.crossdomain(origin='*')(lambda x: x)('foo')
        self.assertEqual(response.status_code, 200)

        self._compare_headers(
            response, '*', ['OPTIONS', 'HEAD', "GET"],
            21600
        )

    def test_decorator_custom_methods(self):
        custom_methods = ["HEAD", "OPTIONS", "GET", "POST", "PATCH"]
        response = decorators.crossdomain(
                origin='*', methods=custom_methods)(
                lambda x: x)('foo')

        self._compare_headers(response, '*', custom_methods,
                              21600)

    def test_custom_headers(self):
        custom_headers = {"CUSTOM-HEADER-KEY"}

        response = decorators.crossdomain(
            origin='*', headers=custom_headers
        )(lambda x: x)('foo')

        self._compare_headers(response, '*', self.methods, 21600)

        self.assertEqual(
            set(custom_headers),
            set(response.headers['Access-Control-Allow-Headers'].split(', '))
        )

    def test_custom_origin(self):
        custom_origins = ['website1', 'website2']
        response = decorators.crossdomain(
            origin=custom_origins
        )(lambda x: x)('foo')

        self._compare_headers(
            response, ', '.join(custom_origins), self.methods, 21600
        )

    def test_max_age(self):
        custom_max_age = 1000

        max_age = timedelta(seconds=custom_max_age)

        response = decorators.crossdomain(
            origin='*',
            max_age=max_age
        )(lambda x: x)('foo')

        self.assertEqual(
            response.headers['Access-Control-Max-Age'],
            str(float(custom_max_age))
        )

    @mock.patch('flask.Flask.make_default_options_response')
    @mock.patch('omicron_server.decorators.request')
    def test_decorator_automatic_options(self, mock_request, mock_default):
        mock_request.method = "OPTIONS"

        decorators.crossdomain(
            origin='*', automatic_options=True
        )(lambda x: x)('foo')

        self.assertTrue(mock_default.called)

    def test_attach_to_all(self):
        response = decorators.crossdomain(origin='*', attach_to_all=False)(
            lambda x: x)('foo')

        access_control_headers = {
            'Access-Control-Allow-Origin', 'Access-Control-Allow-Methods',
            'Access-Control-Max-Age', 'Access-Control-Allow-Headers'
        }

        for header in access_control_headers:
            self.assertNotIn(header, response.headers)
