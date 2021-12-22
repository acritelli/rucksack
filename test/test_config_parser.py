import unittest
from fabric.config import Config
import yaml
from pathlib import Path
from rucksack.config_parser import *
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
  return yaml.safe_load(mock_config)

def mock_find_config_files_in_directory(directory):
  if directory == f"{Path.home()}/.config/rucksack":
    return [f"{Path.home()}/.config/rucksack/file1.yml", f"{Path.home()}/.config/rucksack/file2.yaml"]
  elif directory == '/etc/rucksack':
    return ['/etc/rucksack/file1.yml', '/etc/rucksack/file2.yaml']

def mock_return_config(*args, **kwargs):
  return yaml.safe_load(mock_config)

def mock_raise_oserror(*args, **kwargs):
  raise OSError('Unable to read config file')


def mock_return_empty(*args, **kwargs):
  return {}


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

  @patch('rucksack.config_parser.load_config_from_file', load_config_from_file_cwd)
  def test_load_config_cwd(self):
    config = load_config_from_cwd()
    expected_config = yaml.safe_load(mock_config)
    self.assertEqual(config, expected_config)

  @patch('rucksack.config_parser.find_config_files_in_directory', mock_find_config_files_in_directory)
  @patch('rucksack.config_parser.load_config_from_file', load_config_from_file_cwd)
  def test_load_config_from_home_dir(self):
    config = load_config_from_home_dir()
    expected_config = yaml.safe_load(mock_config)
    self.assertEqual(config, expected_config)

  @patch('rucksack.config_parser.find_config_files_in_directory', mock_find_config_files_in_directory)
  @patch('rucksack.config_parser.load_config_from_file', load_config_from_file_cwd)
  def test_load_config_from_etc_dir(self):
    config = load_config_from_etc_dir()
    expected_config = yaml.safe_load(mock_config)
    self.assertEqual(config, expected_config)

  @patch('rucksack.config_parser.load_config_from_cwd', mock_return_config)
  def test_load_config_main_cwd(self):
    config = load_config()
    expected_config = yaml.safe_load(mock_config)
    self.assertEqual(config, expected_config)

  @patch('rucksack.config_parser.load_config_from_cwd', mock_return_empty)
  @patch('rucksack.config_parser.load_config_from_home_dir', mock_return_config)
  def test_load_config_main_load_config_from_home_dir(self):
    config = load_config()
    expected_config = yaml.safe_load(mock_config)
    self.assertEqual(config, expected_config)

  @patch('rucksack.config_parser.load_config_from_cwd', mock_return_empty)
  @patch('rucksack.config_parser.load_config_from_home_dir', mock_return_empty)
  @patch('rucksack.config_parser.load_config_from_etc_dir', mock_return_config)
  def test_load_config_main_load_config_from_etc_dir(self):
    config = load_config()
    expected_config = yaml.safe_load(mock_config)
    self.assertEqual(config, expected_config)

  @patch('rucksack.config_parser.load_config_from_cwd', mock_return_empty)
  @patch('rucksack.config_parser.load_config_from_home_dir', mock_return_empty)
  @patch('rucksack.config_parser.load_config_from_etc_dir', mock_return_empty)
  @patch('rucksack.config_parser.load_config_from_etc_file', mock_return_config)
  def test_load_config_main_load_config_from_etc_file(self):
    config = load_config()
    expected_config = yaml.safe_load(mock_config)
    self.assertEqual(config, expected_config)

  @patch('rucksack.config_parser.load_config_from_file', mock_return_config)
  def test_load_config_from_specified_file(self):
    config = load_config(file='test')
    expected_config = yaml.safe_load(mock_config)
    self.assertEqual(config, expected_config)

  @patch('rucksack.config_parser.load_config_from_directory', mock_return_config)
  def test_load_config_from_specified_directory(self):
    config = load_config(directory='test')
    expected_config = yaml.safe_load(mock_config)
    self.assertEqual(config, expected_config)

  def test_validate_config(self):
    config = {
      'rucksack-config': {
        'log-level': 'debug',
        'illegal-parameter': 'fail the test'
      }
    }
    self.assertRaises(ConfigParserException, validate_config, config)

    config = {
      "validCommand": ""
    }
    validation_result = validate_config(config)
    self.assertEqual(validation_result, True)

  @patch('rucksack.config_parser.load_config', mock_return_config)
  def test_get_config_config_found(self):
    config = get_config()
    self.assertEqual(config, yaml.safe_load(mock_config))

  @patch('rucksack.config_parser.load_config', mock_return_empty)
  def test_get_config_config_not_found(self):
    self.assertRaises(ConfigNotFoundException, get_config)

  @patch('rucksack.config_parser.find_config_files_in_directory', mock_find_config_files_in_directory)
  @patch('rucksack.config_parser.load_config_from_file', mock_return_config)
  def test_load_config_from_directory(self):
    config = load_config_from_directory('/etc/rucksack')
    self.assertEqual(config, yaml.safe_load(mock_config))

    config = load_config_from_directory('/bad/directory')
    self.assertEqual(config, None)

  @patch('rucksack.config_parser.find_config_files_in_directory', mock_find_config_files_in_directory)
  @patch('rucksack.config_parser.load_config_from_file', mock_raise_oserror)
  def test_load_config_from_directory_exception(self):
    self.assertRaises(ConfigParserException, load_config_from_directory, '/etc/rucksack')
