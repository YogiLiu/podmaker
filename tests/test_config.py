import unittest
from pathlib import Path

from podmaker.config import PMConfig


class TestConfig(unittest.TestCase):
    def setUp(self) -> None:
        self.path = Path(__file__).parent.parent / 'config.example.toml'

    def test_from_file(self) -> None:
        PMConfig.from_file(self.path)
