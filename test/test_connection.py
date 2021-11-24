import unittest
from unittest.mock import patch
from toolbag.connection import *

class MockConnection():
  def __init__(self, host):
    pass

  def open(host):
    pass

  def run(self, *args, **kwargs):
    return True

@patch('toolbag.connection.Connection', MockConnection)
class TestToolbagConnection(unittest.TestCase):

  def test_connection(self):
    my_connection = ToolBagConnection("www.example.com")
    command_result = my_connection.execute_command("whoami")

    self.assertEqual(command_result, True)
