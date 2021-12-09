import logging
from fabric import config
from jinja2 import Environment
from .config_parser import args_list_to_dictionary
from .exceptions import MandatoryArgumentMissingException, UnknownArgumentException, UserWantsToQuitException, ArgumentValueNotProvidedException

logger = logging.getLogger(__name__)

# Given a string and dictionary
# While the string has items: pop an item off the string
  # Can it be found in the current dictionary?
    # Yes
      # Is it a command string?
        # Yes - set the command string variable
        # No
          # Does it have argument options? (e.g., a list etc.)
            # Yes - Present these options to the user
            # No - it must be an argument. Add it to the argument array/dictionary
  # Update the current key and dictionary
def parse_command(requested_command, config):
  current_dictionary = config
  available_args = {}
  command_arguments = {}
  command_config = {}
  command_string = None

  logger.debug(f"Command to parse: {requested_command}")

  # Check to see if the user entered a "special" token
  check_special_command(requested_command)

  while True:
    try:
      current_token = requested_command.pop(0).strip()
      logger.debug(f"Current token: {current_token}")
    except IndexError:
      logger.debug('No more tokens to process')
      break

    # Check to see if we can find the current command in the current dictionary
    # If we can, then we are able to proceed further and see if this is a command,
    # an argument, a category, etc.
    if not command_string:
      logger.debug('Command string is not yet defined')
      try:
        current_dictionary = current_dictionary[current_token]
        logger.debug(f"Current dictionary set to: {current_dictionary}")
      except KeyError:
        pass

    # Check to see if the current dictionary has a "command" key.
    # If it does, then this is a command string
    try:
      if not command_string:
        logger.debug('Command string is not yet defined')
        command_config = current_dictionary
        command_string = current_dictionary['command']
        logger.debug(f"Command string found in current command dictionary: {command_string}")
        continue
    except KeyError:
      logger.debug('No command found in current command dictionary')
      pass

    # If we have found a command string, then remaining keys must be the argument
    # TODO: this doesn't account for a command flag that doesn't take an argument
    if command_string:
      try:
        available_args = args_list_to_dictionary(current_dictionary['args'])
        logger.debug(f"Found arguments for command: {available_args}")
      except KeyError:
        # TODO: Throw exception if an arg is provided but there are no args
        pass
      try:
        # First, make sure we can actually find this argument defined for the command
        # If we find it, then we pop off the next key (the actual argument) and store it
        # in the dictionary
        if current_token in available_args.keys():
          logger.debug(f"'{current_token}' is a valid argument for this command")
          try:
            argument_value = requested_command.pop(0).strip()
          except IndexError:
            logger.warning(f"No value provided for argument: {current_token}")
            raise ArgumentValueNotProvidedException(f"No value provided for argument: {current_token}")
          command_arguments[current_token] = argument_value
          logger.debug(f"Adding '{argument_value}' as the value for the '{current_token}' argument")
        else:
          logger.warning(f"Unknown argument '{current_token}'")
      except KeyError:
        raise UnknownArgumentException(f"Unkown argument: {current_token}")

  # Return three things to the calling function:
  ## 1. The command string itself, which can be passed to a rendering function
  ## 2. A dictionary of arguments, which can also be passed to a rendering function
  ## 3. The config for this entire command, which is useful for doing things like rendering
  ##    default values
  command_dictionary = {
    'command_string': command_string,
    'command_args': command_arguments,
    'command_config': command_config
  }

  logger.debug(f"Returning command dictionary: {command_dictionary}")
  return command_dictionary

def check_special_command(requested_command):
  logger.debug(f"Checking to see if 'requested_command' is a special command.")
  token = requested_command[0].strip()
  if token == "quit":
    logger.debug('"Special command found: quit')
    raise UserWantsToQuitException

def check_mandatory_args(command_dictionary):

  logger.debug(f"Checking mandatory arguments for command dictionary: {command_dictionary}")

  # Check to see if the command should have args. If not, no need to proceed
  try:
    configured_args = args_list_to_dictionary(command_dictionary['command_config']['args'])
  except KeyError:
    logger.debug('Command dictionary does not have any args, so nothing to check.')
    return

  # Iterate through all args for the command and see if any are mandatory
  # If they are, confirm they have been provided
  for configured_arg in configured_args:
    logger.debug(f"Checking to see if '{configured_arg}' is mandatory.")
    try:
      if configured_args[configured_arg]['mandatory']:
        logger.debug(f"Arg '{configured_arg}' is mandatory")
        mandatory_arg_found = False
        for provided_arg in command_dictionary['command_args']:
          if provided_arg == configured_arg:
            logger.debug(f"Found mandatory arg '{configured_arg}' in user provided args.")
            mandatory_arg_found = True

        # If a mandatory arg is not found, see if there is a default for it
        if not mandatory_arg_found:
          logger.debug(f"Mandatory arg '{configured_arg}' not found in user provided args.")
          try:
            configured_args[configured_arg]['default']
            logger.debug(f"Mandatory arg '{configured_arg}' has a default value")
          except KeyError:
            logger.warning(f"Mandatory arg '{configured_arg}' not found in user provided args and has no default value.")
            raise MandatoryArgumentMissingException(f"The mandatory arg {configured_arg} was not provided.")
    except KeyError:
      logger.debug(f"Arg '{configured_arg}' is not mandatory.")
      pass

def render_command(command_dictionary):

  check_mandatory_args(command_dictionary)
  
  template_string = command_dictionary['command_string']

  # For each command argument that is configured for the command, check to see if the user
  # provided a value for it. If so, append its template to the command.
  # We iterate over the config dict first because the order of the arguments matters.
  try:
    for arg in command_dictionary['command_config']['args']:
      logger.debug(f"Checking argument to render: {arg}")
      try:
        # The arg name is the only key in the dictionary, so obtain it.
        arg_name = list(arg)[0]

        try:
          # Get the template string if the arg was provided
          if command_dictionary['command_args'][arg_name]:
            try:
              # Check to see if the arg has a template string.
              # If not, it must be part of the command string, so continue.
              arg_template_string = arg[arg_name]['arg_string']
              logger.debug(f"Found arg template string: {arg_template_string}")
              template_string = f"{template_string} {arg_template_string}"
            except KeyError:
              continue
            continue
        except KeyError:
          # If the arg wasn't provided, then add the default to the command args dictionary
          logger.debug(f"Arg not provided: {arg_name}")
          if arg[arg_name]['mandatory']:
            arg_value = arg[arg_name]['default']
            command_dictionary['command_args'][arg_name] = arg_value
            logger.debug(f"Found default value of '{arg_value}' for arg '{arg_name}")
      except KeyError:
        pass
  except KeyError:
    # If there are no args, then there's nothing to do!
    logger.debug(f"No args for command, nothing to do.")
    pass

  env = Environment()
  template = env.from_string(template_string)
  logger.debug(f"Rendering Jinja2 template: {template_string}")
  return template.render(command_dictionary['command_args'])
