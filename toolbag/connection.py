from fabric import Connection


class ToolBagConnection():
  def __init__(self, host):
    self.host = host
    # TODO: handle localhost
    self.conn = Connection(host)
    self.conn.open()

  def execute_command(self, command):
    if not self.conn:
      # TODO: custom exception
      raise Exception('No host defined yet')

    return self.conn.run(command, warn=True, hide=True)
