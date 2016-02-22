"""
Contains objects for working with the SQL database. This file exports the model
classses, a session object, and a version manager. The purpose of the model
classes is to extract an object-based data model from the underlying DB. The
purpose of the session is to allow transactional interaction with the database.
The purpose of :class:`DatabaseManager` is to provide versioning support for
the DB
"""
from omicron_server.database.models.users import User, Token, Administrator
from omicron_server.database.models.projects import Project
from omicron_server.database.sessions import ContextManagedSession
from omicron_server.database.versioning import DatabaseManager

__author__ = 'Michal Kononenko'
