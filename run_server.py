__author__ = 'Michal Kononenko'
from api_server import app
import config

if __name__ == "__main__":
    app.run(port=config.PORT, debug=config.DEBUG)