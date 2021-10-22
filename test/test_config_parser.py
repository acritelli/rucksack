import os
import unittest
import yaml
from toolbag.config_parser import *
from unittest.mock import patch, mock_open

mock_config = """
---
system:
  get-uptime:
    command: uptime
"""

mock_config_local = """
---
local-test:
  local-command:
    command: test
"""

def mock_glob(file):
  if file == 'fake/*.yml':
    return ['file1.yml']
  if file == 'fake/*.yaml':
    return ['file2.yaml']

def load_config_from_file_local(file, file_type=None):
  if file == f"{os.getcwd()}/toolbag.yml" or file == f"{os.getcwd()}/toolbag.yaml":
    return mock_config_local
  else:
    return None

class TestConfigParser(unittest.TestCase):

  @patch('builtins.open', new_callable=mock_open, read_data=mock_config)
  def test_load_config_from_file(self, mockopen):
    expected_config = yaml.safe_load(mock_config)
    config = load_config_from_file('fake')
    self.assertEqual(config, expected_config)

  @patch('glob.glob', mock_glob)
  def test_find_config_files_in_directory(self):
    files = find_config_files_in_directory('fake')
    self.assertEqual(files, ['file1.yml', 'file2.yaml'])

  @patch('toolbag.config_parser.load_config_from_file', load_config_from_file_local)
  def test_load_config_local(self):
    config = load_config()
    self.assertEqual(config, mock_config_local)
