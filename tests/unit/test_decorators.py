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