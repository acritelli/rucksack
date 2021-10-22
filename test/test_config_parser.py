from toolbag.config_parser import *
from unittest.mock import patch, mock_open
import unittest
import yaml

mock_config = """
---
system:
  get-uptime:
    command: "uptime"
"""

def mock_glob(file):
  if file == 'fake/*.yml':
    return ['file1.yml']
  if file == 'fake/*.yaml':
    return ['file2.yaml']

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
