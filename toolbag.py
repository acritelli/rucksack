import prompt_toolkit
import yaml
from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion

def run_command(command):
  print(f"Run command called on {command}")
  return

def render_command():
  pass

completer_dictionary = {}

with open('./sample_config_updated.yaml', 'r') as file:
  config = yaml.load(file, Loader=yaml.Loader)

print(config)

text = 'system tail-log log_file /var/www/html num_lines 2'

class MyCustomCompleter(prompt_toolkit.completion.Completer):

    def get_completions(self, document, complete_event):
      args_dictionary = None
      requested_command = document.text.split()

      current_dictionary = config
      values_to_yield = config.keys()
      while True:
        try:
          current_term = requested_command.pop(0).strip()
        except IndexError:
          break

        # If we have an args_dictionary, then we've already found the command. No need to keep
        # trying to process the config dict for subcommmands
        if args_dictionary:
          # If the current term is in the args dictionary and has values, present those to the user
          try:
            current_dictionary = args_dictionary[current_term]
          except KeyError:
            # If the current term isn't in the args dictionary, then default to giving the user
            # the list of args
            values_to_yield = args_dictionary.keys()
            continue
        else:
          # If we don't have an args_dictionary, then we haven't found the command yet. Keep
          # diving into the dictionary in an effort to find it.
          try:
            current_dictionary = current_dictionary[current_term]
            values_to_yield = current_dictionary.keys()
          except KeyError:
            # The user must've given us some invalid data. Just return an empty array.
            values_to_yield = []

        # Check to see if this current dictionary has a command key
        # If it does, we're inside a command and everything else is the args
        try:
          if not args_dictionary and current_dictionary['command']:
            args_dictionary = current_dictionary
        except KeyError:
          pass

        # If there is a values field in the current dictionary, then present these to the user
        try:
          values_to_yield = current_dictionary['values']
        except KeyError:
          pass

      if not values_to_yield:
        values_to_yield = args_dictionary.keys()

      for value in values_to_yield:
        if value == 'command':
          continue
        yield Completion(value, start_position=0)

    # def get_completions(self, document, complete_event):
    #   args_dictionary = None
    #   requested_command = document.text.split()

    #   current_dictionary = config
    #   values_to_yield = config.keys()
    #   while True:
    #     try:
    #       current_term = requested_command.pop(0).strip()
    #     except IndexError:
    #       break

    #     try:
    #       # First, check whatever dict we're currently using for the current term.
    #       # If we have it, then it's a category, subcategory, command, etc.
    #       current_dictionary = current_dictionary[current_term]
    #       values_to_yield = current_dictionary.keys()
    #     except KeyError:
    #       # TODO: this could likely be made more efficent by setting a flag once we find a command
    #       # If this key couldn't be found, we're dealing with one of two things:
    #         # An argument name that isn't going to be found by looking into a nested dictionary
    #         # An argument value, which won't be found at all
    #       try:
    #         # See if this current term is in the argument dictionary. If so, we can return those arg values to the user.
    #         current_dictionary = args_dictionary[current_term]
    #       except KeyError:
    #         # If not, then just default to returning the argument dict to the user.
    #         values_to_yield = args_dictionary.keys()
    #         continue

    #     # Check to see if this current dictionary has a command key
    #     # If it does, we're inside a command and everything else is the args
    #     try:
    #       if not args_dictionary and current_dictionary['command']:
    #         args_dictionary = current_dictionary
    #     except KeyError:
    #       pass

    #     # If there is a values field in the current dictionary, then present these to the user
    #     try:
    #       values_to_yield = current_dictionary['values']
    #     except KeyError:
    #       pass

    #   if not values_to_yield:
    #     values_to_yield = args_dictionary.keys()

    #   for value in values_to_yield:
    #     if value == 'command':
    #       continue
    #     yield Completion(value, start_position=0)

text = prompt_toolkit.prompt('> ', completer=MyCustomCompleter())

print(text.split())

requested_command = text.split()
current_dictionary = config
command_string = None
command_arguments = {}

print(requested_command)


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


print(command_string)
print(command_arguments)

quit()
