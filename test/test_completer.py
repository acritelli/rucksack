from unittest import mock
import unittest
import yaml
from toolbag.completer import *
from prompt_toolkit.document import Document


mock_config = """
---
system:
  get-uptime:
    command: "uptime"
  view-boot-log:
    command: "cat {{ log }}"
    log:
      from_command: "find /var/log -name boot.log*"
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

class TestCompleter(unittest.TestCase):

  def test_completer_with_section(self):
    completer = ToolbagCompleter(yaml.load(mock_config, Loader=yaml.Loader))
    document = Document("system")
    yielded_completion = next(completer.get_completions(document, None))
    self.assertEqual(yielded_completion.text, "get-uptime")

  def test_completion_with_values(self):
    completer = ToolbagCompleter(yaml.load(mock_config, Loader=yaml.Loader))
    document = Document("system tail-log log_file")
    yielded_completion = next(completer.get_completions(document, None))
    self.assertEqual(yielded_completion.text, "/var/log/messages")

  def test_completion_with_from_commmand(self):
    completer = ToolbagCompleter(yaml.load(mock_config, Loader=yaml.Loader))
    document = Document("system view-boot-log log")
    yielded_completion = next(completer.get_completions(document, None))
    self.assertEqual(yielded_completion.text, "placeholder")

  def test_completion_with_nothing(self):
    completer = ToolbagCompleter(yaml.load(mock_config, Loader=yaml.Loader))
    document = Document("")
    yielded_completion = next(completer.get_completions(document, None))
    self.assertEqual(yielded_completion.text, "system")

  def test_completion_with_bad_arg(self):
    completer = ToolbagCompleter(yaml.load(mock_config, Loader=yaml.Loader))
    document = Document("system tail-log somearg")
    yielded_completion = next(completer.get_completions(document, None))
    self.assertEqual(yielded_completion.text, "num_lines")

  def test_completion_with_bad_first_term(self):
    completer = ToolbagCompleter(yaml.load(mock_config, Loader=yaml.Loader))
    document = Document("test")
    yielded_completion = next(completer.get_completions(document, None))
    self.assertEqual(yielded_completion.text, '')
