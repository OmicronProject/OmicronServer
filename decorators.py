"""
Contains extensions for the default :class:`flask_restful.Resource`,
that implement decorators for pagination and database sessions
"""
from flask import request
from collections import namedtuple
__author__ = 'Michal Kononenko'

PaginationArgs = namedtuple('PaginationArgs', ['page', 'items_per_page'])


class SessionNotFoundError(AttributeError):
    pass


def restful_pagination(default_items_per_page=1000):
    """
    Wraps a RESTful getter, extracting the arguments ``page`` and ``items_per_page``

    :return:
    """
    def wraps(f):
        def wrapped_function(*args, **kwargs):
            page = request.args.get('page')
            if page is None:
                page = 1
            else:
                try:
                    page = int(page)
                except ValueError:
                    page = 1

            items_per_page = request.args.get('items_per_page')
            if items_per_page is None:
                items_per_page = default_items_per_page
            else:
                try:
                    items_per_page = int(items_per_page)
                except ValueError:
                    items_per_page = default_items_per_page

            pag_args = PaginationArgs(page, items_per_page)

            response = f(pag_args, *args, **kwargs)

            response.headers['page'] = page
            response.headers['items_per_page'] = items_per_page

            return response
        return wrapped_function
    return wraps
