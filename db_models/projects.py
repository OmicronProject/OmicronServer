from db_models import Base
import db_schema
from datetime import datetime

__author__ = 'Michal Kononenko'


class Project(Base):
    """
    Models a project for a given user. The project constructor requires
    the following

    :var str project_name: The name of the project
    :var str description: A description of the project

    """
    __table__ = db_schema.projects

    id = __table__.c.project_id
    name = __table__.c.name
    description = __table__.c.description
    date_created = __table__.c.date_created

    def __init__(
        self, project_name, description,
        date_created=datetime.utcnow(),
        owner=None
    ):
        self.name = project_name
        self.date_created = date_created
        self.owner = owner
        self.description = description

    @property
    def date_created_isoformat(self):
        return self.date_created.isoformat()
