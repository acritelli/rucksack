
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
  command_arguments = {}
  command_string = None

  while True:
    try:
      current_command = requested_command.pop(0).strip()
    except IndexError:
      break

    # Check to see if we can find the current command in the current dictionary
    # If we can, then we are able to proceed further and see if this is a command,
    # an argument, a category, etc.
    if not command_string:
      try:
        current_dictionary = current_dictionary[current_command]
      except KeyError:
        # TODO: This should probably be an error
        pass

    # Check to see if the current dictionary has a "command" key.
    # If it does, then this is a command string
    try:
      if not command_string:
        command_string = current_dictionary['command']
        continue
    except KeyError:
      pass

    # If we have found a command string, then remaining keys must be the argument
    if command_string:
      try:
        print(f"Searching for {current_command} in {current_dictionary.keys()}")
        # First, make sure we can actually find this argument defined for the command
        # If we find it, then we pop off the next key (the actual argument) and store it
        # in the dictionary
        if current_command in current_dictionary.keys():
          command_arguments[current_command] = requested_command.pop(0).strip()
        else:
          continue
      except KeyError:
        # TODO: probably throw some type of error
        pass
  return current_command