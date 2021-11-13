from prompt_toolkit.completion import Completer, Completion
from .config_parser import args_list_to_dictionary

class ToolbagCompleter(Completer):

  def __init__(self, config):
    self.config = config

  def get_completions(self, document, complete_event):
    args_dictionary = None
    requested_command = document.text.split()

    # TODO: consider tracking more state at the class level to reduce duplication.
    # Would need to reset the args dictionary if we exist the args
    # Can do this by storing the position of where we enter the args

    current_dictionary = self.config
    values_to_yield = self.config.keys()
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
          # The user must've given us some invalid data.
          yield

      # Check to see if this current dictionary has a command key
      # If it does, we're inside a command and everything else is the args
      try:
        if not args_dictionary and current_dictionary['command']:
          args_dictionary = args_list_to_dictionary(current_dictionary['args'])
          values_to_yield = args_dictionary
      except KeyError:
        # A command may not have args
        pass

      # If there is a values field in the current dictionary, then present these to the user
      try:
        values_to_yield = current_dictionary['values']
      except KeyError:
        pass

      # If there is a from_command field in the current dictionary, then obtain the appropriate set of values
      # TODO:
      try:
        command_to_execute = current_dictionary['from_command']
        values_to_yield = ['placeholder', 'for', 'command']
      except KeyError:
        pass

    if not values_to_yield and args_dictionary:
      values_to_yield = args_dictionary.keys()

    for value in values_to_yield:
      if value == 'command':
        continue
      yield Completion(value, start_position=0)
