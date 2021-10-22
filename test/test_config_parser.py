from toolbag.config_parser import load_config
import unittest


class TestConfigParser(unittest.TestCase):
  def test_placeholder(self):
      self.assertEqual(7, 7)

  def test_another(self):
    self.assertEqual(6,7)
