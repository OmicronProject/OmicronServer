"""
Script to run the server
"""
from api_server import app
from config import default_config as conf
import logging

__author__ = 'Michal Kononenko'

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

if __name__ == "__main__":
    app.run(port=conf.PORT, debug=conf.DEBUG)