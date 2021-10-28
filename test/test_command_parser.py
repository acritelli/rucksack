import unittest
from toolbag.command_parser import *

# system tail-log log_file /var/log/messages num_lines 10

class TestCommandParser(unittest.TestCase):
  def test_parse_command(self):
    config = {
      'system': {
        'tail-log': {
          'command': 'tail',
          'args': [
            {'log_file': {}},
            {'num_lines': {}}
          ]
        }
      }
    }

    expected_result = {
      'command_string': 'tail',
      'command_args': {'log_file': '/var/log/messages', 'num_lines': '10'},
      'command_config': {
        'command': 'tail',
        'args': [
          {'log_file': {}},
          {'num_lines': {}}
        ]
      }
    }

    command_string = 'system tail-log log_file /var/log/messages num_lines 10'
    self.assertEqual(expected_result,parse_command(command_string.split(), config)
)
