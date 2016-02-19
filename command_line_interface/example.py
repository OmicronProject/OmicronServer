#!/usr/bin/env python

"""
Usage: example.py [ -h | --help ] (TEXT) ...

Options:
    -h, --help  show this
"""

from docopt import docopt

if __name__ == "__main__":
    arguments = docopt(__doc__)
    text = ' '.join(arguments['TEXT'])
    print(text)
