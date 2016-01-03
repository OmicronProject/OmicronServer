"""
Contains classes related to database session management
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
    error-free exit from the context manager
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
        if hasattr(f, '__call__'):
            return self._decorator(f)
        else:
            return self

    def _decorator(self, f):
        def _wrapped_function(*args, **kwargs):
            with self as session:
                new_args = args + (session,)
                response = f(*new_args, **kwargs)
            return response

        _wrapped_function.__name__ = f.__name__
        _wrapped_function.__doc__ = f.__doc__
        return _wrapped_function

    def __enter__(self):
        return self.copy()

    def __exit__(self, exc_type, exc_val, exc_tb):
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
        return '%s(bind=%s, expire_on_commit=%s)' % \
               (self.__class__.__name__, self.bind, self.expire_on_commit)