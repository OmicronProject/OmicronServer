# Welcome to OmicronServer #

**OmicronServer** is the back end for Omicron Web Services, a project that aims
 to automate much of the process engineering and experimentation

## Badges ##

[![Build Status](https://travis-ci.org/MichalKononenko/OmicronServer.svg?branch=ReadmeTravisC)](https://travis-ci.org/MichalKononenko/OmicronServer)
[![Coverage Status](https://coveralls.io/repos/MichalKononenko/OmicronServer/badge.svg?branch=master&service=github)](https://coveralls.io/github/MichalKononenko/OmicronServer?branch=master)
[![GitHub license](https://img.shields.io/badge/License-GNU%20GPL%20v3-blue.svg)]()

## Installation ##
A stable version of **OmicronServer** has not yet been released. TravisCI builds
are run on all branches and pull requests with every commit, but features may be
lacking in these builds. See the issues and project milestones for a timeline
of future releases.

``$ git clone https://github.com/MichalKononenko/OmicronServer.git``
 

## Packages and Dependencies ##
Dependencies are outlined in ``requirements.txt``. In order to install dependencies, run 

``pip install -r requirements.txt``

TravisCI uses this file to install all its dependencies, and Heroku uses this
to identify **OmicronServer** as a [Python](https://docs.python.org/3.5/) project.

Since Travis runs on Linux, it has the advantage of using ``gcc`` to compile
some of the packages listed here. your machine may not have this luxury, and so
you may have to find binaries for the [``psycopg2``](http://initd.org/psycopg/)
package, in order to connect to PostgreSQL

### Supported Versions ###
This project is currently supported for Python versions
- 2.7
- 3.4
- 3.5

### Supported Databases ###
OmicronServer currently supports PostgreSQL and SQLite.

## Running the Program ##

To run the server, run

`` python run_server.py ``

from the command line. 
By default, the server will run on ``localhost:5000``. The address can be specified by
setting the ``IP_ADDRESS`` and ``PORT`` environment variables in your command line.

### Environment Variables ###

The file ``config.py`` will adjust its settings depending on the value of several
environment variables. These are

- ``IP_ADDRESS``: The IP address at which the server is to be hosted
- ``PORT``: The port number at which the server is to be hosted
- ``BASE_DIRECTORY``: The base directory where ``run_server.py`` is kept. By default, this is the current directory of the ``config.py`` file
- ``TOKEN_SECRET_KEY``: The secret key used as a salt to generate authentication tokens for the user. Tokens are not stored on
the back end, but are generated from user data, and the value of ``TOKEN_SECRET_KEY``. If this value is changed, the user's
token will no longer work.
- ``DATABASE_URL``: The URL at which the database sits. This is the database to be used by the server
- ``DEBUG``: If ``TRUE``, then stack traces will be displayed when **in the browser** if the server throws a 500 error
- ``STATE``: A generic flag for specifying between ``DEV``, ``CI``, and ``PROD`` machines. Currently not wired to anything

### Command Line Parsing ###
Unfortunately, the values above must be set as environment variables as OmicronServer does not currently support parsing
these arguments in the command line

## License ##
This project and all files in this repository are licensed under the GNU General Public License (GPL) version 2.
A copy of this license can be found in the ``LICENSE`` file
