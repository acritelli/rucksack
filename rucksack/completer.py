import logging
from prompt_toolkit.completion import Completer, Completion
from functools import lru_cache
from .config_parser import args_list_to_dictionary

logger = logging.getLogger(__name__)

@lru_cache
def get_args_from_command(connection, command):
  # TODO: handle errors
  logger.debug(f"Attempting to obtain arguments from command: {command}")
  result = connection.execute_command(command)
  logger.debug(f"Command result: {result}")
  return result.stdout.splitlines()

class RucksackCompleter(Completer):

  def __init__(self, config, connection):
    self.logger = logging.getLogger(__name__)
    self.config = config
    self.connection = connection

  def get_completions(self, document, complete_event):
    args_dictionary = None
    current_args = set()
    requested_command = document.text.split()
    self.logger.debug(f"Attempting to find completions for: {requested_command}")

    # TODO: consider tracking more state at the class level to reduce duplication.
    # Would need to reset the args dictionary if we exist the args
    # Can do this by storing the position of where we enter the args

    current_dictionary = self.config
    values_to_yield = self.config.keys()
    while True:
      try:
        current_term = requested_command.pop(0).strip()
        self.logger.debug(f"Processing current term: {current_term}")
      except IndexError:
        self.logger.debug(f"No more terms to process in requested command")
        break

      # If we have an args_dictionary, then we've already found the command. No need to keep
      # trying to process the config dict for subcommmands
      if args_dictionary:
        self.logger.debug(f"Args dictionary is currently set: {args_dictionary}")
        self.logger.debug('Checking to see if args dictionary contains current term')
        # If the current term is in the args dictionary and has values, present those to the user
        try:
          # Add this term to a set of current args so that we can avoid presenting
          # duplicate args to the user
          current_dictionary = args_dictionary[current_term]
          self.logger.debug('Term found in args dictionary. Adding to current args set')
          current_args.add(current_term)
          # Ensure that current values to yield (which may be set from previous reference to args dict keys)
          # has any current args removed
          values_to_yield = set(values_to_yield) - current_args
        except KeyError:
          # If the current term isn't in the args dictionary, then default to giving the user
          # the list of args
          self.logger.debug('Term not found in args dictionary.')
          if document.char_before_cursor == ' ':
            self.logger.debug('Character before cursor is a space, yielding all args not yet provided.')
            values_to_yield = set(args_dictionary.keys()) - current_args
            continue
          else:
            self.logger.debug('Non-space character before cursor, user must be typing an arg value.')
            yield Completion("", start_position=0)
      else:
        # If we don't have an args_dictionary, then we haven't found the command yet. Keep
        # diving into the dictionary in an effort to find it.
        self.logger.debug('Args dictionary is not yet set. Continuing to search for command.')
        try:
          current_dictionary = current_dictionary[current_term]
          values_to_yield = current_dictionary.keys()
          self.logger.debug(f"Found current term in dictionary. Yielding: {values_to_yield}")
        except KeyError:
          # The user must've given us some invalid data.
          yield Completion("", start_position=0)

      # Check to see if this current dictionary has a command key
      # If it does, we're inside a command and everything else is the args
      try:
        if not args_dictionary and current_dictionary['command']:
          args_dictionary = args_list_to_dictionary(current_dictionary['args'])
          values_to_yield = set(args_dictionary) - current_args
          self.logger.debug(f"Current dictionary has a command string. Yielding args: {args_dictionary}")
      except KeyError:
        # A command may not have args
        self.logger.debug('Command found, but current dictionary does not have args.')
        pass

      # If there is a values field in the current dictionary, then present these to the user
      try:
        values_to_yield = current_dictionary['values']
        self.logger.debug(f"Current dictionary has values. Yielding: {values_to_yield}")
      except KeyError:
        pass

      # If there is a from_command field in the current dictionary, then obtain the appropriate set of values
      try:
        command_to_execute = current_dictionary['from_command']
        self.logger.debug('Current dictionary has from_command. Attempting to obtain args from command.')
        values_to_yield = get_args_from_command(self.connection, command_to_execute)
        self.logger.debug(f"Received args from command: {values_to_yield}")
      except KeyError:
        pass

    if not values_to_yield and args_dictionary:
      self.logger.debug('No values to yield. Yielding keys of arg dictionary.')
      values_to_yield = set(args_dictionary.keys()) - current_args

    for value in values_to_yield:
      if value == 'command' or value == 'rucksack-config':
        continue
      yield Completion(value, start_position=0)
