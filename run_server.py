"""
Script to run the server
"""
from api_server import app
import config
import logging

__author__ = 'Michal Kononenko'

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

if __name__ == "__main__":
    app.run(port=config.PORT, debug=config.DEBUG)