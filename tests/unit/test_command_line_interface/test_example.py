"""
Testing the basic CLI example which reprints the input
"""
import subprocess
import unittest
from omicron_server.config import default_config as config


class TestExample(unittest.TestCase):
    def setUp(self):
        self.command_to_run = [
            'python',
            '%s/command_line_interface/example.py' % config.BASE_DIRECTORY
            ]

    def test_example(self):
        completed_command = subprocess.Popen(self.command_to_run, stderr=subprocess.PIPE)
        completed_command.wait()
        self.assertEqual(completed_command.returncode, 1)
        self.assertEqual(
            completed_command.stderr.read().decode('utf-8').rstrip(),
            'Usage: example.py [ -h | --help ] (TEXT) ...'
        )


class TestString(unittest.TestCase):
    def setUp(self):
        self.command_to_run = [
            'python',
            '%s/command_line_interface/example.py' % config.BASE_DIRECTORY,
            'HELLO WORLD'
            ]

    def test_string(self):
        completed_command = subprocess.Popen(self.command_to_run, stdout=subprocess.PIPE)
        completed_command.wait()
        self.assertEqual(completed_command.returncode, 0)
        self.assertEqual(completed_command.stdout.read().decode('utf-8').rstrip(), 'HELLO WORLD')


class TestHelp(unittest.TestCase):
    def setUp(self):
        self.command_to_run = [
            'python',
            '%s/command_line_interface/example.py' % config.BASE_DIRECTORY,
            '-h'
            ]

    def test_help(self):
        completed_command = subprocess.Popen(self.command_to_run, stdout=subprocess.PIPE)
        completed_command.wait()
        self.assertEqual(completed_command.returncode, 0)
        self.assertIsNotNone(completed_command.stdout)
