from jinja2 import Environment
from .config_parser import args_list_to_dictionary
from .exceptions import MandatoryArgumentMissingException, UnknownArgumentException, UserWantsToQuitException

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

  # Check to see if the user entered a "special" token
  check_special_command(requested_command)

  while True:
    try:
      current_token = requested_command.pop(0).strip()
    except IndexError:
      break

    # Check to see if we can find the current command in the current dictionary
    # If we can, then we are able to proceed further and see if this is a command,
    # an argument, a category, etc.
    if not command_string:
      try:
        current_dictionary = current_dictionary[current_token]
      except KeyError:
        pass

    # Check to see if the current dictionary has a "command" key.
    # If it does, then this is a command string
    try:
      if not command_string:
        command_config = current_dictionary
        command_string = current_dictionary['command']
        continue
    except KeyError:
      pass

    # If we have found a command string, then remaining keys must be the argument
    # TODO: this doesn't account for a command flag that doesn't take an argument
    if command_string:
      try:
        available_args = args_list_to_dictionary(current_dictionary['args'])
      except KeyError:
        # TODO: Throw exception if an arg is provided but there are no args
        pass
      try:
        # First, make sure we can actually find this argument defined for the command
        # If we find it, then we pop off the next key (the actual argument) and store it
        # in the dictionary
        if current_token in available_args.keys():
          command_arguments[current_token] = requested_command.pop(0).strip()
        else:
          raise UnknownArgumentException(f"Unkown argument: {current_token}")
          continue
      except KeyError:
        print('arg not found')
        pass
  return {
    'command_string': command_string,
    'command_args': command_arguments,
    'command_config': command_config
  }

def check_special_command(requested_command):
  token = requested_command[0].strip()
  if token == "quit":
    raise UserWantsToQuitException

def check_mandatory_args(command_dictionary):

  # Check to see if the command should have args. If not, no need to proceed
  try:
    configured_args = args_list_to_dictionary(command_dictionary['command_config']['args'])
  except KeyError:
    return

  # Iterate through all args for the command and see if any are mandatory
  # If they are, confirm they have been provided
  for configured_arg in configured_args:
    try:
      if configured_args[configured_arg]['mandatory']:
        mandatory_arg_found = False
        for provided_arg in command_dictionary['command_args']:
          if provided_arg == configured_arg:
            mandatory_arg_found = True

        if not mandatory_arg_found:
          raise MandatoryArgumentMissingException(f"The mandatory arg {configured_arg} was not provided.")
    except KeyError:
      pass

def render_command(command_dictionary):

  check_mandatory_args(command_dictionary)
  
  template_string = command_dictionary['command_string']

  # For each command argument that is configured for the command, check to see if the user
  # provided a value for it. If so, append its template to the command.
  # We iterate over the config dict first because the order of the arguments matters.
  try:
    for arg in command_dictionary['command_config']['args']:
      try:
        # The arg name is the only key in the dictionary, so obtain it.
        arg_name = list(arg)[0]
        arg_value = command_dictionary['command_args'][arg_name]

        # If the config has a template string for this arg, then get it. Otherwise, default
        # to {{ argname }}
        try:
          arg_template_string = arg[arg_name]['arg_string']
          template_string = f"{template_string} {arg_template_string}"
        except KeyError:
          pass
      except KeyError:
        pass
  except KeyError:
    # If there are no args, then there's nothing to do!
    pass

  env = Environment()
  template = env.from_string(template_string)
  return template.render(command_dictionary['command_args'])
