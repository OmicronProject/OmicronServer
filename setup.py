#!/usr/bin/env python
from setuptools import setup
import omicron_server

setup(
    name='OmicronServer',
    version=omicron_server.__version__,
    author=omicron_server.__author__,
    author_email='mkononen@uwaterloo.ca',
    maintainer='MichalKononenko',
    maintainer_email='mkononen@uwaterloo.ca',
    description='The back end to the Omicron Project stack.',
    license=omicron_server.__license__,
    url='https://github.com/MichalKononenko/OmicronServer',
    packages=['omicron_server']
    )
