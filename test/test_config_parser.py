import os
import unittest
from unittest import mock
import yaml
from pathlib import Path
from toolbag.config_parser import *
from unittest.mock import patch, mock_open

mock_config = """
---
system:
  get-uptime:
    command: uptime
"""

def mock_glob(file):
  if file == 'fake/*.yml':
    return ['file1.yml']
  if file == 'fake/*.yaml':
    return ['file2.yaml']

def load_config_from_file_cwd(file):
  # if file == f"{os.getcwd()}/toolbag.yml" or file == f"{os.getcwd()}/toolbag.yaml":
  #   return yaml.safe_load(mock_config)
  # elif file == f"{Path.home()}/.config/toolbag/file1.yml" or f"{Path.home()}/.config/toolbag/file2.yaml":
  #   return yaml.safe_load(mock_config)
  # elif file == '/etc/toolbag/file1.yml' or file 
  # else:
  return yaml.safe_load(mock_config)

def mock_find_config_files_in_directory(directory):
  if directory == f"{Path.home()}/.config/toolbag":
    return [f"{Path.home()}/.config/toolbag/file1.yml", f"{Path.home()}/.config/toolbag/file2.yaml"]
  elif directory == '/etc/toolbag':
    return ['/etc/toolbag/file1.yml', '/etc/toolbag/file2.yaml']


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

  @patch('toolbag.config_parser.load_config_from_file', load_config_from_file_cwd)
  def test_load_config_cwd(self):
    config = load_config_from_cwd()
    expected_config = yaml.safe_load(mock_config)
    self.assertEqual(config, expected_config)

  @patch('toolbag.config_parser.find_config_files_in_directory', mock_find_config_files_in_directory)
  @patch('toolbag.config_parser.load_config_from_file', load_config_from_file_cwd)
  def test_load_config_from_home_dir(self):
    config = load_config_from_home_dir()
    expected_config = yaml.safe_load(mock_config)
    self.assertEqual(config, expected_config)

  @patch('toolbag.config_parser.find_config_files_in_directory', mock_find_config_files_in_directory)
  @patch('toolbag.config_parser.load_config_from_file', load_config_from_file_cwd)
  def test_load_config_from_etc_dir(self):
    config = load_config_from_etc_dir()
    expected_config = yaml.safe_load(mock_config)
    self.assertEqual(config, expected_config)
