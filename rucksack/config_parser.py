import glob
import logging
import os
import yaml
from pathlib import Path
from .exceptions import ConfigParserException, ConfigNotFoundException

logger = logging.getLogger(__name__)

def args_list_to_dictionary(args_list):
  logger.debug(f"Converting arg list to dictionary: {args_list}")
  args_dictionary = {}
  for item in args_list:
    arg_name = list(item.keys())[0]
    args_dictionary[arg_name] = item[arg_name]
  logger.debug(f"Returning arg dictionary: {args_dictionary}")
  return args_dictionary

def load_config_from_file(file=None):
  logger.debug(f"Attempting to load config from file: {file}")
  with open(file, 'r') as config_file:
    config = yaml.load(config_file, Loader=yaml.Loader)
    logger.debug(f"Config loaded from file. Returning config: {config}")
    return config

# TODO: utilize this function elsewhere and DRY out code
def load_config_from_directory(directory):
  logger.debug(f"Attempting to load config file from directory: {directory}")
  config = {}
  files = find_config_files_in_directory(directory)
  if files:
    logger.debug(f"Found config files in directory: {directory}")
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
    logger.debug(f"No config files found in {directory}") 

def find_config_files_in_directory(directory=None):
  logger.debug(f"Attempting to find config files in directory {directory}")
  files = []
  files += glob.glob(f"{directory}/*.yml")
  files += glob.glob(f"{directory}/*.yaml")
  logger.debug(f"Config files in directory: {files}")
  return files

def load_config_from_cwd():
  logger.debug('Attempting to load config file from current working directory')
  config = {}
  file = f"{os.getcwd()}/rucksack.yml"
  try:
    config = load_config_from_file(file)
    logger.debug('Successfully loaded config file from CWD rucksack.yml')
  except OSError:
    logger.debug(f"Unable to read config file {file}")
    pass

  file = f"{os.getcwd()}/rucksack.yaml"
  try:
    config = load_config_from_file(file)
    logger.debug('Successfully loaded config file from CWD rucksack.yaml')
  except OSError:
    logger.debug(f"Unable to read config file {file}")
    pass

  return config

def load_config_from_home_dir():
  logger.debug('Attempting to load config file from home directory')
  config = {}
  files = find_config_files_in_directory(f"{Path.home()}/.config/rucksack")
  if files:
    logger.debug(f"Found config files in home {Path.home()}/.config/rucksack")
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
  logger.debug('Attempting to load config file from /etc/rucksack directory')
  config = {}
  files = find_config_files_in_directory('/etc/rucksack')
  if files:
    logger.debug('Found config files in /etc/rucksack')
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
def load_config(file=None, directory=None):
  config = {}

  # Attempt to load from a file or directory if provided
  if file:
    config = load_config_from_file(file)
    return config
  if directory:
    config = load_config_from_directory(directory)
    return config
  

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

  if 'rucksack-config' in config.keys():
    validate_rucksack_config(config['rucksack-config'])

  # TODO: more validation would be great (e.g., ensuring a command only has valid keys, etc.)
  return True

def validate_rucksack_config(config):
  # TODO: these are CLI args, so eliminate them from config
  allowed_keys = {'log-level', 'log-file'}
  illegal_keys = set(config.keys()) - allowed_keys
  if illegal_keys:
    raise ConfigParserException(f"Illegal keys found in rucksack-config: {illegal_keys}")

def get_config(file=None, directory=None):
  config = load_config(file, directory)
  if not config:
    raise ConfigNotFoundException("No valid configuration file found.")
  validate_config(config)
  return config
