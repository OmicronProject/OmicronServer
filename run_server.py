"""
Script to run the server
"""
from api_server import app
from config import default_config as conf
from db_models import metadata
import subprocess
import logging
import os

__author__ = 'Michal Kononenko'

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

if __name__ == "__main__":
    metadata.create_all(bind=conf.DATABASE_ENGINE)

    os.environ['PYTHONPATH'] = \
        '%s;%s' % (conf.BASE_DIRECTORY, os.environ['PYTHONPATH'])
    subprocess.call(['alembic', 'upgrade', 'head'])

    app.run(host=conf.IP_ADDRESS, port=conf.PORT, debug=conf.DEBUG)
