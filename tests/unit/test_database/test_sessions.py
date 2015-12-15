import unittest

import mock
from sqlalchemy import create_engine

import database.sessions

__author__ = 'Michal Kononenko'


class TestContextManagedSession(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///')
        self.base_session = database.sessions.ContextManagedSession(bind=self.engine)

    def test_context_managed_session_enter(self):
        with self.base_session() as session:
            self.assertNotEqual(self.base_session, session)
            self.assertEqual(self.base_session.__dict__, session.__dict__)

    def test_exit_no_error(self):
        commit = mock.MagicMock()
        rollback = mock.MagicMock()
        with self.base_session() as session:
            session.commit = commit
            session.rollback = rollback

        self.assertFalse(rollback.called)
        self.assertEqual(commit.call_args, mock.call())

    def test_exit_with_error(self):
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
        repr_string = '%s(bind=%s, expire_on_commit=%s)' % \
                      (self.base_session.__class__.__name__,
                       self.base_session.bind,
                       self.base_session.expire_on_commit)

        self.assertEqual(repr_string, self.base_session.__repr__())


class TestSessionDecorator(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///')
        self.base_session = database.sessions.ContextManagedSession(bind=self.engine)

    def test_decorator_callable(self):
        @self.base_session()
        def _test_decorator(created_session):
            return created_session

        session = _test_decorator()
        self.assertIsInstance(session,
                              database.sessions.ContextManagedSession)
        self.assertNotEqual(session, self.base_session)

    def test_context_manager(self):
        with self.base_session() as session:
            pass

        self.assertIsInstance(session,
                              database.sessions.ContextManagedSession)
        self.assertNotEqual(session, self.base_session)