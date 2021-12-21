import logging
from fabric import Connection


class RucksackConnection():
  def __init__(self, host):
    self.host = host
    self.logger = logging.getLogger(__name__)
    self.logger.debug(f"Attempting to open connection with hosts: {host}")
    self.conn = Connection(host)

    # Connections are lazy, so eagerly open the connection (as long as it isn't to localhost)
    if host in ['localhost', '127.0.0.1']:
      pass
    else: 
      self.conn.open()
    self.logger.debug(f"Opened connection with host {host}")

  def execute_command(self, command):
    self.logger.debug(f"Attempting to execute command: {command}")

    if self.host in ['localhost', '127.0.0.1']:
        return self.conn.local(command, warn=True, hide=True)
    else:
      return self.conn.run(command, warn=True, hide=True)
