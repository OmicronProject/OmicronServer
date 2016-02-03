"""
Contains unit tests for :mod:`views.projects`
"""
import unittest
import mock
from api_server import app
from database import Project, User
import json
from datetime import datetime
from views import Projects

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
    @mock.patch('auth._verify_user', return_value=True)
    def test_get(self, mock_auth, mock_count, mock_all):
        project_list = [self.project]

        mock_all.return_value = project_list
        mock_count.return_value = len(project_list)

        r = self.request_method(self.url, headers=self.headers)

        self.assertEqual(200, r.status_code)

        self.assertTrue(mock_count.called)
        self.assertTrue(mock_all.called)
        self.assertTrue(mock_auth.called)


@mock.patch('api_server.auth.verify_password_callback', return_value=True)
class TestCreateProject(TestProjectView):
    def setUp(self):
        self.request_method = self.client.post
        self.url = 'api/v1/projects'

    @mock.patch('sqlalchemy.orm.Query.first')
    @mock.patch('sqlalchemy.orm.Session.add')
    def test_post(self, mock_add, mock_first, mock_auth):
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
        self.assertTrue(mock_auth.called)

    def test_post_bad_data(self, mock_auth):
        data_to_post = {
            'not_a_valid_key': 'foo',
            'description': self.project_description,
            'owner': self.owner_name
        }

        r = self.request_method(self.url, data=json.dumps(data_to_post),
                                headers=self.headers)

        self.assertEqual(r.status_code, 400)
        self.assertTrue(mock_auth.called)

    @mock.patch('sqlalchemy.orm.Query.first')
    def test_post_no_owner(self, mock_first, mock_auth):
        mock_first.return_value = None

        data_to_post = {
            'name': 'test_project',
            'description': 'This is a description',
            'owner': self.owner_name
        }

        r = self.request_method(self.url, data=json.dumps(data_to_post),
                                headers=self.headers)

        self.assertEqual(r.status_code, 400)
        self.assertTrue(mock_auth.called)


class TestDedicatedProject(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.project_name = 'Test Project'
        self.project_description = 'Test Description'
        self.date_created = datetime.utcnow()
        self.project = Project(self.project_name, self.project_description,
                               self.date_created)

        self.project_id = 1
        self.template_url = '/api/v1/projects/%s'
        self.headers = {'Content-Type': 'application/json'}


class TestDedicatedProjectGet(TestDedicatedProject):
    def setUp(self):
        TestDedicatedProject.setUp(self)
        self.request_method = self.client.get

    @mock.patch('auth._verify_user', return_value=True)
    @mock.patch('sqlalchemy.orm.Query.first')
    def test_get_int_username(self, mock_first, mock_verify_user):
        mock_first.return_value = self.project

        with app.test_request_context(self.template_url % self.project_id):
            p = Projects()
            response = p.get(self.project_id)
            self.assertEqual(response.status_code, 200)
        self.assertTrue(mock_verify_user.called)

    @mock.patch('auth._verify_user', return_value=True)
    @mock.patch('sqlalchemy.orm.Query.first')
    def test_get_str_username(self, mock_first, mock_verify_user):
        mock_first.return_value = self.project

        with app.test_request_context(self.template_url % self.project_name):
            p = Projects()
            response = p.get(self.project_name)
            self.assertEqual(response.status_code, 200)
        self.assertTrue(mock_verify_user.called)


class TestDedicatedProjectDelete(TestDedicatedProject):

    def setUp(self):
        TestDedicatedProject.setUp(self)
        self.request_method = self.client.delete

    @mock.patch('auth._verify_user', return_value=True)
    @mock.patch('sqlalchemy.orm.Query.first')
    @mock.patch('sqlalchemy.orm.Session.delete')
    def test_delete_int_project(
            self, mock_delete, mock_first, mock_verify_user
    ):
        mock_first.return_value = self.project

        with app.test_request_context(self.template_url % self.project_id):
            p = Projects()
            response = p.delete(self.project_id)

            self.assertEqual(response.status_code, 200)

        self.assertTrue(mock_verify_user.called)

        self.assertEqual(mock.call(self.project), mock_delete.call_args)

    @mock.patch('auth._verify_user', return_value=True)
    @mock.patch('sqlalchemy.orm.Query.first')
    @mock.patch('sqlalchemy.orm.Session.delete')
    def test_delete_str_project(
            self, mock_delete, mock_first, mock_verify_user
    ):
        mock_first.return_value = self.project

        with app.test_request_context(self.template_url % self.project_name):
            p = Projects()
            response = p.delete(self.project_name)

            self.assertEqual(response.status_code, 200)

        self.assertTrue(mock_verify_user.called)
        self.assertEqual(mock.call(self.project), mock_delete.call_args)
