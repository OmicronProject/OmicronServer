"""
Contains unit tests for :mod:`views.projects`
"""
import unittest
import mock
from api_server import app
from database import Project, User

__author__ = 'Michal Kononenko'


class TestProjectView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        cls.headers = {'content-type': 'application/json'}

        cls.owner_name = 'Bilbo Baggins'
        cls.owner_password = 'gandalf'
        cls.owner_email = 'bilbo@bag_end.com'
        cls.owner = User(cls.owner_name, cls.owner_password, cls.owner_email)

        cls.project_name = 'Test Project'
        cls.project_description = 'Project Description with some **Markdown**'
        cls.project = Project(cls.project_name, cls.project_description)


class TestGet(TestProjectView):

    def setUp(self):
        self.request_method = self.client.get
        self.url = 'api/v1/projects'

    @mock.patch('sqlalchemy.orm.Query.all')
    @mock.patch('sqlalchemy.orm.Query.count')
    def test_get(self, mock_count, mock_all):
        project_list = [self.project]

        mock_all.return_value = project_list
        mock_count.return_value = len(project_list)

        r = self.request_method(self.url, headers=self.headers)

        self.assertEqual(200, r.status_code)

        self.assertTrue(mock_count.called)
        self.assertTrue(mock_all.called)
