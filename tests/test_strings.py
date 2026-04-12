import sys
import unittest
from unittest.mock import MagicMock, patch

class TestStrings(unittest.TestCase):
    @patch.dict('sys.modules', {'simpleeval': MagicMock(), 'helpers.files': MagicMock()})
    def test_format_key(self):
        # We must import after patching sys.modules locally
        from helpers.strings import format_key
        self.assertEqual(format_key("camelCase"), "Camel Case")
        self.assertEqual(format_key("snake_case"), "Snake Case")
        self.assertEqual(format_key("PascalCase"), "Pascal Case")
        self.assertEqual(format_key("kebab-case"), "Kebab Case")
        self.assertEqual(format_key("already Title Case"), "Already Title Case")
        self.assertEqual(format_key("mixOf_camel_and-kebab"), "Mix Of Camel And Kebab")
        self.assertEqual(format_key("thisIsATest"), "This Is Atest")

if __name__ == "__main__":
    unittest.main()
