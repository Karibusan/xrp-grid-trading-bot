import unittest
from src.config_loader import load_config

class TestConfigLoader(unittest.TestCase):
    def test_config_is_dict(self):
        config = load_config()
        self.assertIsInstance(config, dict)