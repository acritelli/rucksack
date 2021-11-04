import unittest
from toolbag.command_parser import *
from toolbag.exceptions import MandatoryArgumentMissingException

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

  def test_check_mandatory_args(self):
    # Test with mandatory arg missing
    command_dictionary = {'command_string': 'tail', 'command_args': {}, 'command_config': {'command': 'tail', 'args': [{'num_lines': {'arg_string': '-n {{ num_lines }}'}}, {'log_file': {'mandatory': True}}]}}
    self.assertRaises(MandatoryArgumentMissingException, check_mandatory_args, command_dictionary)

    # Test with mandatory arg provided
    command_dictionary = {'command_string': 'tail', 'command_args': {'log_file': '/var/log/messages'}, 'command_config': {'command': 'tail', 'args': [{'num_lines': {'arg_string': '-n {{ num_lines }}'}}, {'log_file': {'mandatory': True}}]}}
    check_mandatory_args(command_dictionary)

    # Test with no args
    command_dictionary = {'command_string': 'uptime', 'command_args': {}, 'command_config': {'command': 'uptime'}}
    check_mandatory_args(command_dictionary)

  def test_check_special_command(self):
    command = ['quit', 'whatever']
    self.assertRaises(UserWantsToQuitException, check_special_command, command)


