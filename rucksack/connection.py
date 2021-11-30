import logging
from fabric import Connection


class RucksackConnection():
  def __init__(self, host):
    self.host = host
    self.logger = logging.getLogger(__name__)
    self.logger.debug(f"Attempting to open connection with hosts: {host}")
    # TODO: handle localhost
    self.conn = Connection(host)
    self.conn.open()
    self.logger.debug(f"Opened connection with host {host}")

  def execute_command(self, command):
    self.logger.debug(f"Attempting to execute command: {command}")
    if not self.conn:
      # TODO: custom exception
      self.logger.critical('Cannot execute command. Host connection has not yet been established.')
      raise Exception('No host defined yet')

    return self.conn.run(command, warn=True, hide=True)
