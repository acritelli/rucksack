import argparse
import prompt_toolkit
import logging
import sys
from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion, FuzzyCompleter
from toolbag.completer import ToolbagCompleter
from toolbag.command_parser import parse_command, render_command
from toolbag.connection import ToolBagConnection

from toolbag import config_parser
from toolbag.exceptions import UserWantsToQuitException

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

  while True:
    text = prompt_toolkit.prompt(f"{args.host}> ",  completer=FuzzyCompleter(ToolbagCompleter(config)))

    requested_command = text.split()

    if not requested_command:
      continue

    try:
      command_string = parse_command(requested_command, config)
      print(command_string)
    except UserWantsToQuitException:
      print('Goodbye!')
      quit()

    rendered_command = render_command(command_string)
    print(f"Attempting to run {rendered_command}")
    print(conn.execute_command(rendered_command))

if __name__ == '__main__':
  while True:
    try:
      main()
    except (KeyboardInterrupt, EOFError):
      print('Goodbye!')
      quit()
