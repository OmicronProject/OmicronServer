"""
Contains model classes related to managing projects on the Omicron server
"""
from datetime import datetime
from omicron_server.database.models import Base
from omicron_server.database import schema

__author__ = 'Michal Kononenko'


class Project(Base):
    """
    Models a project for a given user. The project constructor requires
    the following

    :var str project_name: The name of the project
    :var str description: A description of the project
    :var datetime.datetime date_created: The date at which the project was
        created, defaults to the current datetime
    :var User owner: The user who owns this project
    """
    __table__ = schema.projects

    id = __table__.c.project_id
    name = __table__.c.name
    description = __table__.c.description
    date_created = __table__.c.date_created

    def __init__(
        self, project_name, description,
        date_created=datetime.utcnow(),
        owner=None
    ):
        """
        Instantiates the variables described above
        """
        self.name = project_name
        self.date_created = date_created
        self.owner = owner
        self.description = description

    @property
    def date_created_isoformat(self):
        """
        Returns the project date created as an `ISO 8601`_ - compliant string
        :return: The date string
        :rtype: str

        .. _ISO 8601: https://en.wikipedia.org/wiki/ISO_8601
        """
        return self.date_created.isoformat()

    @property
    def get(self):
        """
        Returns a dictionary representing a summary of the project.
        :return: A summary of the project
        :rtype: dict
        """
        return {
            'name': self.name,
            'description': self.description,
            'date_created': self.date_created,
            'owner': self.owner.get if self.owner is not None else 'None'
        }
