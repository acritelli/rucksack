import unittest
import yaml
from rucksack.completer import *
from prompt_toolkit.document import Document
from invoke.runners import Result


mock_config = """
---
rucksack-config:
  somevalue: 'test'
system:
  get-uptime:
    command: "uptime"
  view-auth-log:
    command: "cat"
    args:
      - log:
          from_command: "find /var/log -name '*auth.log*' | grep -v '.gz'"
  tail-log:
    command: "tail"
    args:
      - num_lines:
         arg_string: -n {{ num_lines }}
      - log_file:
          mandatory: True
          values:
            - /var/log/messages
            - /var/log/kern.log
            - /var/log/auth.log
apache:
  get-ips:
    command: "tail /var/log/apache2/access_log"
    args:
      - num_lines:
          arg_string: -n {{ num_lines }}
nginx:
  reload:
    command: 'kill -HUP $(pidof nginx)'
"""

class MockConnection():
  def execute_command(self, command):
    return Result(stdout='/var/log/auth.log')

class TestCompleter(unittest.TestCase):

  def test_completer_with_section(self):
    completer = RucksackCompleter(yaml.load(mock_config, Loader=yaml.Loader), None)
    document = Document("system")
    yielded_completion = next(completer.get_completions(document, None))
    self.assertEqual(yielded_completion.text, "get-uptime")

  def test_completion_with_values(self):
    completer = RucksackCompleter(yaml.load(mock_config, Loader=yaml.Loader), None)
    document = Document("system tail-log log_file")
    yielded_completion = next(completer.get_completions(document, None))
    self.assertEqual(yielded_completion.text, "/var/log/messages")

  def test_completion_with_from_commmand(self):
    completer = RucksackCompleter(yaml.load(mock_config, Loader=yaml.Loader), MockConnection())
    document = Document("system view-auth-log log")
    yielded_completion = next(completer.get_completions(document, None))
    self.assertEqual(yielded_completion.text, "/var/log/auth.log")

  def test_completion_with_nothing(self):
    completer = RucksackCompleter(yaml.load(mock_config, Loader=yaml.Loader), None)
    document = Document("")
    yielded_completion = next(completer.get_completions(document, None))
    self.assertEqual(yielded_completion.text, "system")

  def test_completion_with_bad_arg(self):
    completer = RucksackCompleter(yaml.load(mock_config, Loader=yaml.Loader), None)
    document = Document("system tail-log somearg ")
    yielded_completion = next(completer.get_completions(document, None))
    self.assertIn(yielded_completion.text, ['num_lines', 'log_file'])

  def test_completion_with_bad_first_term(self):
    completer = RucksackCompleter(yaml.load(mock_config, Loader=yaml.Loader), None)
    document = Document("test")
    yielded_completion = next(completer.get_completions(document, None))
    self.assertEqual(yielded_completion.text, '')

  def test_completion_with_user_typing_arg_value(self):
    completer = RucksackCompleter(yaml.load(mock_config, Loader=yaml.Loader), None)
    document = Document("system tail-log log_file /var/lo")
    yielded_completion = next(completer.get_completions(document, None))
    self.assertEqual(yielded_completion.text, '')
