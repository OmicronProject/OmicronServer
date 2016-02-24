#!/usr/bin/env python
from setuptools import setup
import omicron_server

setup(
    name='omicron_server',
    version=omicron_server.__version__,
    author=omicron_server.__author__,
    author_email='mkononen@uwaterloo.ca',
    maintainer='Michal Kononenko',
    maintainer_email='mkononen@uwaterloo.ca',
    description='The back end to the Omicron Project stack.',
    license=omicron_server.__license__,
    url='https://github.com/MichalKononenko/OmicronServer',
    packages=[
        'omicron_server',
        'omicron_server.command_line_interface',
        'omicron_server.views',
        'omicron_server.database',
        'omicron_server.database.models'
    ],
    include_package_data=True,
    package_data={'omicron_server': [
        'schemas/*.json',
        'schemas/projects/*.json',
        'schemas/projects-project_id-file/*.json',
        'schemas/token/*.json',
        'schemas/users/*.json',
        'schemas/users-user_id/*.json'
        ]}
    )
