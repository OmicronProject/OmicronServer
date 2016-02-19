"""
Testing the basic CLI example which reprints the input
"""

import unittest
import subprocess

class TestExample(unittest.TestCase):
    def setUp(self):
        self.command_to_run = 'python ../../../command_line_interface/example.py'

    def test_example(self):
        completed_command = subprocess.run(self.command_to_run,stderr=subprocess.PIPE)
        self.assertEqual(completed_command.returncode, 1)
        self.assertEqual(completed_command.stderr.decode("utf-8").rstrip(), 'Usage: example.py [ -h | --help ] (TEXT) ...')

class TestString(unittest.TestCase):
    def setUp(self):
        self.command_to_run = 'python ../../../command_line_interface/example.py HELLO WORLD'

    def test_string(self):
        completed_command = subprocess.run(self.command_to_run,stdout=subprocess.PIPE)
        self.assertEqual(completed_command.returncode,0)
        self.assertEqual(completed_command.stdout.decode("utf-8").rstrip(),'HELLO WORLD')

class TestHelp(unittest.TestCase):
    def setUp(self):
        self.command_to_run = 'python ../../../command_line_interface/example.py -h'

    def test_help(self):
        completed_command = subprocess.run(self.command_to_run,stdout=subprocess.PIPE)
        print(completed_command.stdout)
        self.assertEqual(completed_command.returncode,0)
        self.assertIsNotNone(completed_command.stdout)