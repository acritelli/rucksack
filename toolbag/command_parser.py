from jinja2 import Environment
from .config_parser import args_list_to_dictionary

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
        # TODO: This should probably be an error
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
      available_args = args_list_to_dictionary(current_dictionary['args'])
      try:
        # First, make sure we can actually find this argument defined for the command
        # If we find it, then we pop off the next key (the actual argument) and store it
        # in the dictionary
        if current_token in available_args.keys():
          command_arguments[current_token] = requested_command.pop(0).strip()
        else:
          continue
      except KeyError:
        # TODO: probably throw some type of error
        pass
  return {
    'command_string': command_string,
    'command_args': command_arguments,
    'command_config': command_config
  }

def render_command(command_dictionary):
  
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
        except KeyError:
          arg_template_string = '{{ ' + arg_name + ' }}'

        template_string = f"{template_string} {arg_template_string}"
      except KeyError:
        pass
  except KeyError:
    # If there are no args, then there's nothing to do!
    pass

  env = Environment()
  template = env.from_string(template_string)
  return template.render(command_dictionary['command_args'])
