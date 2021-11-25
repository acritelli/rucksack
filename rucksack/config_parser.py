import glob
import logging
import os
import yaml
from pathlib import Path
from .exceptions import ConfigParserException, ConfigNotFoundException

logger = logging.getLogger('rucksack')
logger.setLevel(logging.DEBUG)

def args_list_to_dictionary(args_list):
  args_dictionary = {}
  for item in args_list:
    arg_name = list(item.keys())[0]
    args_dictionary[arg_name] = item[arg_name]
  return args_dictionary

def load_config_from_file(file=None):
  with open(file, 'r') as config_file:
    config = yaml.load(config_file, Loader=yaml.Loader)
    return config

def find_config_files_in_directory(directory=None):
  files = []
  files += glob.glob(f"{directory}/*.yml")
  files += glob.glob(f"{directory}/*.yaml")
  return files

def load_config_from_cwd():
  config = {}
  file = f"{os.getcwd()}/rucksack.yml"
  try:
    config = load_config_from_file(file)
  except OSError:
    logger.debug(f"Unable to read config file {file}")
    pass

  file = f"{os.getcwd()}/rucksack.yaml"
  try:
    config = load_config_from_file(file)
  except OSError:
    logger.debug(f"Unable to read config file {file}")
    pass

  return config

def load_config_from_home_dir():
  config = {}
  logger.debug(f"Searching for config files in {Path.home()}/.config/rucksack")
  files = find_config_files_in_directory(f"{Path.home()}/.config/rucksack")
  if files:
    for file in files:
      try:
        temp_dict = load_config_from_file(file)
        for key in temp_dict.keys():
          config[key] = temp_dict[key]
      except OSError as e:
        logger.debug(f"Unable to read config file {file}")
        raise ConfigParserException(f"Unable to read config file {file}") from e
    return config
  else:
    logger.debug(f"No config files found in {Path.home()}/.config/rucksack")

def load_config_from_etc_dir():
  config = {}
  logger.debug(f"Searching for config files in /etc/rucksack")
  files = find_config_files_in_directory('/etc/rucksack')
  if files:
    for file in files:
      try:
        temp_dict = load_config_from_file(file)
        for key in temp_dict.keys():
          config[key] = temp_dict[key]
      except OSError as e:
        logger.critical(f"Unable to read config file {file}")
        raise ConfigParserException(f"Unable to read config file {file}") from e
    return config
  else:
    logger.debug(f"No config files found in /etc/rucksack")

def load_config_from_etc_file():
  config = {}
  try:
    config = load_config_from_file(f"{Path.home()}/.config/rucksack/rucksack.yml")
  except OSError:
    logger.debug(f"Unable to read config file {Path.home()}/.config/rucksack/rucksack.yml")
    pass

  try:
    config = load_config_from_file(f"{Path.home()}/.config/rucksack/rucksack.yaml")
  except OSError:
    logger.debug(f"Unable to read config file {Path.home()}/.config/rucksack/rucksack.yaml")
    pass

  return config

# Config file search order
## Skipped if the user passes a config directory or file
## Any match halts the search process)
### 1. Look for rucksack.[yml|yaml] in local directory
### 2. Search ~/.config/rucksack for yaml or yml files. Load all files.
### 3. Look for ~/.config/rucksack.[yml|yaml]
### 4. Search /etc/rucksack for yaml or yml files. Load all files.
def load_config():
  config = {}

  config = load_config_from_cwd()
  if config:
    return config

  config = load_config_from_home_dir()
  if config:
    return config

  config = load_config_from_etc_dir()
  if config:
    return config

  config = load_config_from_etc_file()
  if config:
    return config

def validate_config(config):
  # Reserve "config" top level for special use
  if 'config' in config.keys():
    raise ConfigParserException('"config" cannot be a top-level key in config file')
  # TODO: more validation would be great (e.g., ensuring a command only has valid keys, etc.)
  return True

def get_config():
  config = load_config()
  if not config:
    raise ConfigNotFoundException("No valid configuration file found.")
  validate_config(config)
  return config