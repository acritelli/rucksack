import unittest
from rucksack.command_parser import *
from rucksack.exceptions import MandatoryArgumentMissingException

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

  def test_render_command(self):

    command_dictionary = {
      'command_string': 'tail {{ log_file }}',
      'command_args': {
        'num_lines': '5'
        },
        'command_config': {
          'command': 'tail {{ log_file }}',
          'args': [
            {
              'num_lines': {
                'arg_string': '-n {{ num_lines }}'
                }
            },
            {
              'log_file': {
                'mandatory': True,
                'default': '/var/log/syslog',
                'values': ['/var/log/syslog', '/var/log/kern.log', '/var/log/auth.log']
                }
            }
          ]
        }
      }

    expected_result = 'tail /var/log/syslog -n 5'

    self.assertEqual(render_command(command_dictionary), expected_result)

  def test_render_command_no_args(self):
    command_dictionary = {'command_string': 'uptime', 'command_args': {}, 'command_config': {'command': 'uptime'}}
    expected_result = 'uptime'
    self.assertEqual(render_command(command_dictionary), expected_result)



