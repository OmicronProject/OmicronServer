"""
Contains global config parameters for the API
"""
__author__ = 'Michal Kononenko'


STATE = 'DEV'

if STATE == 'DEV':
    DEBUG = True
    PORT = 5000
elif STATE == 'CI':
    DEBUG = True
    PORT = 5000
else:
    STATE = 'PROD'
    DEBUG = 'FALSE'
    PORT = 5000
