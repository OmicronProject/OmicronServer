import unittest
from datetime import datetime

from omicron_server.database import Project

__author__ = 'Michal Kononenko'


class TestProject(unittest.TestCase):

    def setUp(self):
        self.project_name = 'test_project'
        self.project_description = 'This is a description'
        self.date_created = datetime.utcnow()


class TestProjectConstructor(TestProject):

    def test_constructor(self):
        project = Project(
            self.project_name, self.project_description,
            self.date_created
        )

        self.assertIsInstance(project, Project)
        self.assertEqual(project.name, self.project_name)
        self.assertEqual(project.description, self.project_description)
        self.assertEqual(project.date_created_isoformat,
                         self.date_created.isoformat()
        )
