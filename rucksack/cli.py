import logging
import sys
from prompt_toolkit import PromptSession, print_formatted_text
from prompt_toolkit.completion import FuzzyCompleter
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.styles import Style
from rucksack.completer import RucksackCompleter
from rucksack.command_parser import parse_command, render_command
from rucksack.connection import RucksackConnection
from rucksack.config_parser import get_config
from rucksack.exceptions import ConfigNotFoundException, UnknownArgumentException, UserWantsToQuitException, MandatoryArgumentMissingException


class RucksackCli():

  def __init__(self, host, config_file=None):
    self.host = host
    self.logger = logging.getLogger(__name__)

    self.logger.debug('Creating new RucksackCLI')

    # TODO: read this only once and accept as an arg
    try:
      self.logger.debug('Attempting to get configuration')
      self.config = get_config(config_file)
    except ConfigNotFoundException as e:
      print(e)
      quit(1)

    self.logger.debug(f"Attempting to create a RucksackConnection to {host}")
    self.conn = RucksackConnection(self.host)


  # Sets the color of the command prompt based on whether or not there was an error
  # Command prompt is red on error, white otherwise
  # TODO: would be cool to customize this via config
  def set_prompt(self, command_error):

    if command_error:
      parser_color = 'red'
    else:
      parser_color = 'white'

    style = Style.from_dict({
        'prompt': parser_color,
    })

    message = [
        ('class:prompt', f"{self.host}> ")
    ]

    return {
      "message": message,
      "style": style
    }

  def start(self):

    session = PromptSession()

    command_error = None

    while True:

      text = session.prompt(**self.set_prompt(command_error), completer=FuzzyCompleter(RucksackCompleter(self.config, self.conn)))

      requested_command = text.split()
      self.logger.debug(f"User entered requested command f{requested_command}")

      if not requested_command:
        self.logger.debug('User did not enter a command')
        continue

      try:
        command_string = parse_command(requested_command, self.config)
        self.logger.debug(f"Command parsed as {command_string}")
      except UnknownArgumentException as e:
          self.logger.debug('Command parsing failed')
          text = FormattedText([
              ('red', str(e)),
          ])
          print_formatted_text(text)
          continue 
      except UserWantsToQuitException:
        print('Goodbye!')
        quit()

      if command_string['command_string']:
        try:
          rendered_command = render_command(command_string)
          self.logger.debug(f"Command rendered as: {rendered_command}")
        except MandatoryArgumentMissingException as e:
          text = FormattedText([
              ('red', str(e)),
          ])
          print_formatted_text(text)
          continue
      else:
        text = FormattedText([
            ('red', 'No such command'),
        ])

        print_formatted_text(text)
        continue
      self.logger.info(f"Attempting to run: {rendered_command}")
      print(f"Attempting to run {rendered_command}")
      result = self.conn.execute_command(rendered_command)

      self.logger.debug(f"Command result: {result}")

      if result.stderr:
        command_error = True
      else:
        command_error = False


      text = FormattedText([
          ('green', result.stdout),
          ('', '\n'),
          ('red', result.stderr),
      ])

      print_formatted_text(text)
