"""
Script to run the server
"""
from api_server import app
from config import default_config as conf
from db_models import metadata, User, sessionmaker
import logging
import os

__author__ = 'Michal Kononenko'

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

if __name__ == "__main__":
    metadata.create_all(bind=conf.DATABASE_ENGINE)

    os.environ['PYTHONPATH'] = \
        '%s;%s' % (conf.BASE_DIRECTORY, os.environ['PYTHONPATH'])

    with sessionmaker(engine=conf.DATABASE_ENGINE) as session:
        user = session.query(User).filter_by(username=conf.ROOT_USER).first()
        if not user:
            user = User(conf.ROOT_USER, conf.ROOT_PASSWORD, conf.ROOT_EMAIL)
            session.add(user)

    app.run(host=conf.IP_ADDRESS, port=conf.PORT, debug=conf.DEBUG)