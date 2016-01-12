"""
Contains classes related to session management with the DB.
"""
from sqlalchemy.orm import Session
import logging
__author__ = 'Michal Kononenko'

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class ContextManagedSession(Session):
    """
    An extension to :class:`sqlalchemy.orm.Session` that allows the session
    to be run using a ``with`` statement, committing all changes on an
    error-free exit from the context manager.

    This class also allows deep copies of itself to be injected dynamically
    into function arguments, when employed as a decorator.

    .. note::

        In order to make the best use of :class:`ContextManagedSession`, it is
        recommended that this class is first instantiated in a module-level
        scope, with its ``bind`` (i.e. the SQLAlchemy `engine`_ or
        connection to which the session is bound), declared in as global a
        scope as possible. In particular, engines should be declared as
        globally as possible in order to maximize the efficiency of
        SQLAlchemy's `connection pooling`_ features.

        The module-level instantiation is then used as a master from which
        copies are created as needed.

    ** Example **

    The following example shows how to use the session as both a context
    manager and a decorator

    .. code-block:: python


        import engine # import the DB engine from somewhere else if needed

        session = ContextManagedSession(bind=engine)

        @session()
        def do_something(session):
            session.query(something)

        def do_something_context_managed():

            with session() as new_session:
                new_session.query(something)

    .. _engine: http://docs.sqlalchemy.org/en/latest/core/engines.html
    .. _connection pooling: http://goo.gl/tIJ33L
    """
    def copy(self):
        """
        Returns a new :class:`ContextManagedSession` with the same namespace
        as ``self``
        """
        session = self.__class__()
        session.__dict__ = self.__dict__
        return session

    def __call__(self, f=None):
        """
        Returns itself, provided that the argument ``f`` is not a callable
        function. (i.e., it does not have a ``__call__`` `method`_ defined)

        :param f: The function to be decorated. If no function is provided,
            then f is ``None``.
        :type f: function or None
        :return: A deep copy of this session, or a decorator function that
            can then inject arguments dynamically into the function to be
            decorated.
        :rtype: :class:`ContextManagedSession` or a function

        .. _method: http://goo.gl/qCr2Uk
        """
        if hasattr(f, '__call__'):
            return self._decorator(f)
        else:
            return self

    def _decorator(self, f):
        """
        This method decorates a function f with the session to be run. This
        is done by invoking the :class:`ContextManagedSession`'s context
        manager to open and clean up a new session, and running the
        decorated function in this context. The session is then appended to
        the decorated function's argument list, and the function is then run.

        For reconciling method names and docstring for documentation
        purposes, and to avoid namespace collisions in the server's routing
        table, the ``__name__`` and ``__doc__`` properties of the decorated
        function are assigned to the decorator.

        :param function f: The function to decorate
        :return: A function that decorates the function to be decorated
        :rtype: function
        """
        def _wrapped_function(*args, **kwargs):
            """
            Wraps the function to be decorated. This function opens the
            context manager and runs ``f`` provided from
            :meth:`ContextManagedSession._decorator`'s scope, with the
            arguments and keyword arguments passed into f.

            :param args: The arguments with which the decorated function
                ``f`` was called.
            :param kwargs: The keyword arguments with which the decorated
                ``f`` was called.
            :return: The return value of the function ``f``, when run with
                the session from the new context appended to the argument list.
            """
            with self as session:
                new_args = args + (session,)
                response = f(*new_args, **kwargs)
            return response

        _wrapped_function.__name__ = f.__name__
        _wrapped_function.__doc__ = f.__doc__
        return _wrapped_function

    def __enter__(self):
        """
        Magic method that opens a new context for the session, returning a
        deep copy of the session to use in the new context.

        :return: A deep copy of ``self``
        :rtype: :class:`ContextManagedSession`
        """
        return self.copy()

    def __exit__(self, exc_type, exc_val, _):
        """
        Magic method that is responsible for exiting the context created in
        :meth:`ContextManagedSession.__enter__`; running the required
        clean-up logic in order to flush changes made in the session to the
        database.

        If there are no exceptions thrown in the
        :class:`ContextManagedSession`'s context, it is assumed that the
        code inside the context completed successfully. In this case,
        the changes made to the database in this session will be committed.

        If an exception was thrown in this context, then the database will
        be rolled back to the state before any logic inside the context manager
        will be executed.

        The arguments taken into this method are the standard arguments
        taken into an ``__exit__`` `method`_.

        The last argument ``_`` is used as a placeholder for the stack trace
        of the exception thrown in the context. This parameter is
        currently not used in this method, as re-throwing an exception
        prepends the stack trace of the exception prior to re-throw into the
        exception. Python is awesome this way :)!

        .. _method: http://goo.gl/ZHXkZ4

        :param type exc_type: The class of exception that was thrown in the
            context. This is ``None`` if no exception was thrown
        :param exc_type exc_val: The particular instance of the exception that
            was thrown during execution in the context. After the session is
            rolled back, this exception is re-thrown.
        """
        if exc_type is None:
            try:
                self.commit()
            except BaseException as exc:
                log.error('Session commit raised error %s', exc)
                self.rollback()
                raise exc
        else:
            self.rollback()
            raise exc_val

    def __repr__(self):
        """
        Returns a string representation of an instance of
        :class:`ContextManagedSession` useful for debugging.

        :return: A string representing useful data about an instance of this
            class
        :rtype: str
        """
        return '%s(bind=%s, expire_on_commit=%s)' % \
               (self.__class__.__name__, self.bind, self.expire_on_commit)
