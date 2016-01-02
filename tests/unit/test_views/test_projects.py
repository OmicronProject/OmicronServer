"""
Contains unit tests for :mod:`views.projects`
"""
import unittest
import mock
from api_server import app
from database import Project, User
import json

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


class TestCreateProject(TestProjectView):
    def setUp(self):
        self.request_method = self.client.post
        self.url = 'api/v1/projects'

    @mock.patch('sqlalchemy.orm.Query.first')
    @mock.patch('sqlalchemy.orm.Session.add')
    def test_post(self, mock_add, mock_first):
        mock_first.return_value = self.owner

        data_to_post = {
            'name': self.project_name,
            'description': self.project_description,
            'owner': self.owner_name
        }

        r = self.request_method(self.url, data=json.dumps(data_to_post),
                                headers=self.headers)
        self.assertEqual(r.status_code, 201)

        self.assertEqual(mock.call(), mock_first.call_args)
        self.assertTrue(mock_add.called)

    def test_post_bad_data(self):
        data_to_post = {
            'not_a_valid_key': 'foo',
            'description': self.project_description,
            'owner': self.owner_name
        }

        r = self.request_method(self.url, data=json.dumps(data_to_post),
                                headers=self.headers)

        self.assertEqual(r.status_code, 400)
