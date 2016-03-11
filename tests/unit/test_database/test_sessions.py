"""
Contains unit tests for :mod:`database.sessions`
"""
import mock
from sqlalchemy import create_engine
from tests import TestCaseWithAppContext
from omicron_server.database import ContextManagedSession

__author__ = 'Michal Kononenko'


class TestContextManagedSession(TestCaseWithAppContext):
    """
    Base test case for :class:`database.sessions.ContextManagedSession`
    """
    def setUp(self):
        """
        Create an engine for a SQLlite in-memory DB, and create a
        :class:`ContextManagedSession` to test on
        """
        TestCaseWithAppContext.setUp(self)
        self.engine = create_engine('sqlite:///')
        self.base_session = ContextManagedSession(bind=self.engine)

    def test_context_managed_session_enter(self):
        """
        Test that entering a :class:`ContextManagedSession` creates a new
        object of the same type as :class:`ContextManagedSession`, that the
        namespaces of the new session is equal to the master session,
        but that they are different objects, (i.e. reside at different
        memory addresses)
        """
        with self.base_session() as session:
            self.assertNotEqual(self.base_session, session)
            self.assertEqual(self.base_session.__dict__, session.__dict__)
            self.assertIsInstance(session, self.base_session.__class__)

    def test_exit_no_error(self):
        """
        Tests that upon exiting the context manager,
        :meth:`sqlalchemy.orm.Session.commit` is called.
        """
        commit = mock.MagicMock()
        rollback = mock.MagicMock()
        with self.base_session() as session:
            session.commit = commit
            session.rollback = rollback

        self.assertFalse(rollback.called)
        self.assertEqual(commit.call_args, mock.call())

    def test_exit_with_error(self):
        """
        Tests that if an exception is thrown inside the context manager,
        the rollback method is called, and the exception is re-thrown
        """
        error_to_raise = Exception('test_error')
        commit = mock.MagicMock()
        rollback = mock.MagicMock()

        with self.assertRaises(error_to_raise.__class__):
            with self.base_session() as session:
                session.commit = commit
                session.rollback = rollback
                raise Exception('test_error')

        self.assertFalse(commit.called)
        self.assertEqual(rollback.call_args, mock.call())

    def test_exit_commit_error(self):
        """
        Tests that :meth:`sqlalchemy.orm.Session.rollback` is called if
        there is an error on execution of
        :meth:`sqlalchemy.orm.Session.commit`.
        """
        error_to_raise = Exception('test_error')
        commit = mock.MagicMock(side_effect=error_to_raise)
        rollback = mock.MagicMock()

        with self.assertRaises(error_to_raise.__class__):
            with self.base_session() as session:
                session.commit = commit
                session.rollback = rollback

        self.assertTrue(commit.called)
        self.assertTrue(rollback.called)

    def test_repr(self):
        """
        Tests :meth:`database.sessions.ContextManagedSession.__repr__`
        """
        repr_string = '%s(bind=%s, expire_on_commit=%s)' % \
                      (self.base_session.__class__.__name__,
                       self.base_session.bind,
                       self.base_session.expire_on_commit)

        self.assertEqual(repr_string, self.base_session.__repr__())

    def test_decorator_callable(self):
        """
        Tests that :class:`database.sessions.ContextManagedSession` is able to
        decorate a function.
        """
        @self.base_session()
        def _test_decorator(created_session):
            return created_session

        session = _test_decorator()
        self.assertIsInstance(session, ContextManagedSession)
        self.assertNotEqual(session, self.base_session)

    def test_context_manager(self):
        """
        Test that the session is able to work as a context manager
        """
        with self.base_session() as session:
            pass

        self.assertIsInstance(session, ContextManagedSession)
        self.assertNotEqual(session, self.base_session)
