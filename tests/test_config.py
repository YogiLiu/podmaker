import sys
import unittest
from pathlib import Path

from podmaker.config import PMConfig

if sys.version_info >= (3, 11):
    import tomllib as toml
else:
    import tomlkit as toml


class TestConfig(unittest.TestCase):
    def setUp(self) -> None:
        self.path = Path(__file__).parent.parent / 'config.example.toml'

    def test_from_file(self) -> None:
        config = PMConfig.from_file(self.path)
        self.assertEqual(config.model_dump(mode='json'), toml.loads(self.path.read_text()))
