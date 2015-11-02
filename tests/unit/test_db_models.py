"""
Contains unit tests for :mod:`db_models`
"""
import unittest
import unittest.mock as mock
import db_models as models

__author__ = 'Michal Kononenko'


class TestSessionMaker(unittest.TestCase):

    @mock.patch('db_models.sqlalchemy_sessionmaker')
    def test_sessionmaker_no_args(self, mock_sessionmaker):
        mock_session = mock.MagicMock()
        mock_sessionmaker.return_value = mock_session

        mock_sessionmaker_call = mock.call(bind=models.sqlalchemy_engine)

        self.assertEqual(mock_session, models.sessionmaker())
        self.assertEqual(mock_sessionmaker.call_args, mock_sessionmaker_call)

    @mock.patch('db_models.sqlalchemy_sessionmaker')
    def test_sessionmaker_with_engine(self, mock_sessionmaker):
        mock_session = mock.MagicMock()
        mock_sessionmaker.return_value = mock_session

        mock_engine = mock.MagicMock()
        mock_sessionmaker_call = mock.call(bind=mock_engine)

        self.assertEqual(mock_session, models.sessionmaker(mock_engine))
        self.assertEqual(mock_sessionmaker.call_args, mock_sessionmaker_call)
