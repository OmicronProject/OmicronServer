"""
Contains code to start an instance of the OmicronServer API under Apache
"""
from api_server import app as application
import sys
from config import default_config as conf

sys.path.insert(0, conf.BASE_DIRECTORY)

