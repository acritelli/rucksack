import prompt_toolkit
import logging
import yaml
import sys
from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion, FuzzyCompleter
from toolbag.completer import ToolbagCompleter
from toolbag.command_parser import parse_command

from toolbag import config_parser

logger = logging.getLogger()

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def run_command(command):
  print(f"Run command called on {command}")
  return

def render_command():
  pass

def main():
  completer_dictionary = {}

config = config_parser.get_config()

print(config)

text = prompt_toolkit.prompt('> ', completer=FuzzyCompleter(ToolbagCompleter(config)))

print(text.split())

requested_command = text.split()
current_dictionary = config
command_string = None
command_arguments = {}

print(requested_command)

command_string = parse_command(requested_command, config)


print(f"The command string is {command_string}")
# print(command_arguments)

if __name__ == '__main__':
  while True:
    try:
      main()
    except (KeyboardInterrupt, EOFError):
      print('Goodbye!')
      quit()
