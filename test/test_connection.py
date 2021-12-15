import unittest
from unittest.mock import patch
from rucksack.connection import *

class MockConnection():
  def __init__(self, host):
    pass

  def open(host):
    pass

  def run(self, *args, **kwargs):
    return True

  def local(self, *args, **kwargs):
    return True

@patch('rucksack.connection.Connection', MockConnection)
class TestToolbagConnection(unittest.TestCase):

  def test_connection(self):
    my_connection = RucksackConnection("www.example.com")
    command_result = my_connection.execute_command("whoami")

    self.assertEqual(command_result, True)

@patch('rucksack.connection.Connection', MockConnection)
class TestToolbagLocalConnection(unittest.TestCase):

  def test_connection(self):
    my_connection = RucksackConnection("localhost")
    command_result = my_connection.execute_command("whoami")

    self.assertEqual(command_result, True)
