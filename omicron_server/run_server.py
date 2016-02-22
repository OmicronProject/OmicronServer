"""
Script to run the server
"""
import logging
import os

from omicron_server import app
from omicron_server.database.models.users import Administrator
from omicron_server.database.sessions import ContextManagedSession

from omicron_server.config import default_config as conf
from omicron_server.database.schema import metadata

__author__ = 'Michal Kononenko'

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

db_session = ContextManagedSession(bind=conf.DATABASE_ENGINE)


@db_session()
def create_root_user(session):
    """
    If no root user is found in the DB, it makes a root user with
    the credentials given in the config

    :param ContextManagedSession session: The session to be used for making
        the root user
    """
    user = session.query(Administrator).filter_by(
            username=conf.ROOT_USER).first()
    if not user:
        user = Administrator(
                conf.ROOT_USER, conf.ROOT_PASSWORD, conf.ROOT_EMAIL
        )
        session.add(user)

if __name__ == "__main__":
    metadata.create_all(bind=conf.DATABASE_ENGINE)

    os.environ['PYTHONPATH'] = \
        '%s;%s' % (conf.BASE_DIRECTORY, os.environ['PYTHONPATH'])

    create_root_user()

    app.run(host=conf.IP_ADDRESS, port=conf.PORT, debug=conf.DEBUG)
