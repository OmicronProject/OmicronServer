import unittest
from sqlalchemy import create_engine
from db_schema import metadata
from datetime import datetime
from db_models.projects import Project

__author__ = 'Michal Kononenko'

class TestProject(unittest.TestCase):

    engine = create_engine('sqlite:///')

    @classmethod
    def setUpClass(cls):
        metadata.create_all(bind=cls.engine)

    def setUp(self):
        self.project_name = 'test_project'
        self.project_description = 'This is a description'
        self.date_created = datetime.utcnow()

    @classmethod
    def tearDownClass(cls):
        metadata.drop_all(bind=cls.engine)


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
