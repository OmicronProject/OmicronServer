#!/usr/bin/env python
from setuptools import setup

__author__ = 'Michal Kononenko'
__license__ = "GPL-3.0"
__version__ = '0.1'

setup(
    name='omicron_server',
    version=__version__,
    author=__author__,
    author_email='mkononen@uwaterloo.ca',
    maintainer='Michal Kononenko',
    maintainer_email='mkononen@uwaterloo.ca',
    description='The back end to the Omicron Project stack.',
    license=__license__,
    url='https://github.com/MichalKononenko/OmicronServer',
    packages=['omicron_server']
    )
