class ConfigParserException(Exception):
  pass

class MandatoryArgumentMissingException(Exception):
  pass

class UserWantsToQuitException(Exception):
  pass

class UnknownArgumentException(Exception):
  pass

class ArgumentValueNotProvidedException(Exception):
  pass

class ConfigNotFoundException(Exception):
  pass
