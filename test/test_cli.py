import unittest
from prompt_toolkit.formatted_text import FormattedText
from unittest.mock import patch
from rucksack.cli import *

config = {
  'uptime': {
    'command': 'uptime'
  },
  'tail-log': {
    'command': 'tail {{ logfile }}',
    'args': [
      { 'logfile': {'mandatory': True} }
    ]
  },
  'gimme-an-error': {
    'command': 'false'
  }
}

# I know, I know: global variables
# The command array array allows the MockPromptSession to pop off commands provided by tests
# The output array stores output from all mocked command executions, so it can be compared to
# expected output
commands = []
output = []

# Class to mock session. Primarily used to mock sending a user command by popping a command
# off the commands array
class MockPromptSession():

  def prompt(self, *args, **kwargs):
    return commands.pop(0)

# Simple mock for command output
class MockCommandOutput():
  def __init__(self, stdout, stderr):
    self.stdout = stdout
    self.stderr = stderr

# TODO: this is copy/pasted from test_connection
class MockConnection():
  def __init__(self, host):
    pass

  def local(self, command, **kwargs):
    if command == 'false':
      return MockCommandOutput('', 'bad stuff')
    else:
      return MockCommandOutput('mockoutput', '')

def mock_get_config(*args, **kwargs):
  return config

def mock_get_config_with_error(*args, **kwargs):
  raise ConfigNotFoundException('Configuration not found')

# Throws stdout/stderr into a variable that can be examined later
def mock_print_formatted_text(text, **kwargs):
  global output
  output.append(text)
class TestCLI(unittest.TestCase):

  @patch('rucksack.cli.get_config', mock_get_config)
  @patch('rucksack.cli.PromptSession', MockPromptSession)
  @patch('rucksack.connection.Connection', MockConnection)
  @patch('rucksack.cli.print_formatted_text', mock_print_formatted_text)
  def run_cli_test(self, commands_to_execute, expected_output):
    global commands
    global output
    output = []
    commands = commands_to_execute
    ruck_cli = RucksackCli('localhost')
    self.assertRaises(UserWantsToQuitException, ruck_cli.start)
    self.assertEqual(output, expected_output)

  def test_valid_command(self):
    commands_to_execute = ['uptime', 'quit']
    expected_output = ['Attempting to run uptime', FormattedText([('green', 'mockoutput')]), FormattedText([('red', '')])]
    self.run_cli_test(commands_to_execute, expected_output)

  def test_no_command(self):
    commands_to_execute = ['', 'quit']
    expected_output = []
    self.run_cli_test(commands_to_execute, expected_output)

  def test_bad_command(self):
    commands_to_execute = ['wrongcommand', 'quit']
    expected_output = [FormattedText([('red', 'No such command')])]
    self.run_cli_test(commands_to_execute, expected_output)

  def test_missing_mandatory_arg(self):
    commands_to_execute = ['tail-log', 'quit']
    expected_output = [FormattedText([('red', 'The mandatory arg logfile was not provided.')])]
    self.run_cli_test(commands_to_execute, expected_output)

  def test_missing_arg_value(self):
    commands_to_execute = ['tail-log logfile', 'quit']
    expected_output = [FormattedText([('red', 'No value provided for argument: logfile')])]
    self.run_cli_test(commands_to_execute, expected_output)

  def test_command_with_error(self):
    commands_to_execute = ['gimme-an-error', 'quit']
    expected_output = ['Attempting to run false', FormattedText([('green', '')]), FormattedText([('red', 'bad stuff')])]
    self.run_cli_test(commands_to_execute, expected_output)

  @patch('rucksack.cli.get_config', mock_get_config_with_error)
  def test_config_not_found(self):
    self.assertRaises(ConfigNotFoundException, RucksackCli, 'localhost')
