import argparse
import prompt_toolkit
import logging
import sys
from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion, FuzzyCompleter
from toolbag.completer import ToolbagCompleter
from toolbag.command_parser import parse_command, render_command
from toolbag.connection import ToolBagConnection
from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.styles import Style

from toolbag import config_parser
from toolbag.exceptions import UserWantsToQuitException, MandatoryArgumentMissingException

logger = logging.getLogger('toolbag')

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def main():

  parser = argparse.ArgumentParser()
  parser.add_argument('host')

  args = parser.parse_args()

  conn = ToolBagConnection(args.host)

  # TODO: read this only once.
  config = config_parser.get_config()

  parser_color = 'white'
  command_error = False

  while True:

    if command_error:
      parser_color = 'red'
    else:
      parser_color = 'white'

    style = Style.from_dict({
        'prompt': parser_color,
    })

    message = [
        ('class:prompt', f"{args.host}> ")
    ]


    text = prompt_toolkit.prompt(message,  style=style, completer=FuzzyCompleter(ToolbagCompleter(config, conn)))

    requested_command = text.split()

    if not requested_command:
      continue

    try:
      command_string = parse_command(requested_command, config)
    except UserWantsToQuitException:
      print('Goodbye!')
      quit()

    if command_string['command_string']:
      try:
        rendered_command = render_command(command_string)
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
    print(f"Attempting to run {rendered_command}")
    result = conn.execute_command(rendered_command)

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

if __name__ == '__main__':
  while True:
    try:
      main()
    except (KeyboardInterrupt, EOFError):
      print('Goodbye!')
      quit()
