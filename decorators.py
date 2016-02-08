"""
Contains utilities to decorate endpoints with additional functionality

Decorators
~~~~~~~~~~

A decorator_ is a function that takes in a function as an argument, and
returns a function. In Python, a typical decorator can be used as follows

.. code-block:: python

    class UserContainer(Resource):
        @staticmethod
        def parse_search_params(params):
            pass

        @restful_pagination()
        def get(self, pag_args):
            pass

The use of the ``@`` symbol is syntactic sugar for

 .. code-block:: python

    parse_search_params = staticmethod(parse_search_params)

In order to provide arguments to the decorator, as in the case of
``@restful_pagination``, another level of indirection is needed.
``restful_pagination`` is not a decorator in and of itself, but it returns a
decorator that then decorates a particular function.

.. note::
    Due to `Sphinx Autodoc <http://sphinx-doc.org/ext/autodoc.html>`'s
    documentation generator, the :attr:`__name__` and :attr:`__doc__` property
    of the function to be decorated must be assigned to the :attr:`__name__`
    and :attr:`__doc__` of the decorator. See
    :class:`tests.unit.test_decorators.TestRestfulPagination` for an example
    of a unit test that tests this behaviour

.. _decorator: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
"""
from collections import namedtuple
from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper

__author__ = 'Michal Kononenko'

PaginationArgs = namedtuple(
    'PaginationArgs', ['page', 'items_per_page', 'offset']
)


def restful_pagination(default_items_per_page=1000):
    """
    Wraps a RESTful getter, extracting the arguments
    ``page`` and ``items_per_page`` from the URL query parameter.
    These arguments are then parsed into integers, and returned as a
    `named tuple <https://docs.python.org/2/library/collections.html#collections.namedtuple>`_.
    consisting of the following variables

        - :attr:`page`: The number of the page to be displayed
        - :attr:`items_per_page`: The number of items to be displayed on each
            page
        - :attr:`offset`: The offset (item number of the first item on this
            page)

    The `PaginationArgs` tuple is then injected into the decorated function as
    a keyword argument (kwarg_.), in a similar way to the ``@mock.patch``
    decorator. A usage pattern for this decorator could be

    .. code-block:: python

        @restful_pagination()
        def paginated_input(pagination_args):
            with sessionmaker() as session:
                session.query(Something).limit(
                    pagination_args.limit
                ).offset(
                    pagination_args.offset
                ).all()

    :param default_items_per_page: The number of items that should be displayed
        by default. This is to prevent a query with, for example, 300,000
        results loading a large amount of data into memory.
    :return: A decorator with the default arguments per page configured
    :rtype: function

    .. _kwarg: https://stackoverflow.com/questions/1769403/understanding-kwargs-in-python

    """
    def _wraps(f):
        _wraps.__name__ = f.__name__
        _wraps.__doc__ = f.__doc__

        def _wrapped_function(*args, **kwargs):
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

            offset = (page - 1) * items_per_page - 1

            pag_args = PaginationArgs(
                page, items_per_page, offset
            )

            new_args = args + (pag_args,)

            response = f(*new_args, **kwargs)

            response.headers['page'] = page
            response.headers['items_per_page'] = items_per_page

            return response
        _wrapped_function.__name__ = f.__name__
        _wrapped_function.__doc__ = f.__doc__
        return _wrapped_function
    return _wraps

def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, str):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, str):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator