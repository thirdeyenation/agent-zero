import unittest
import asyncio
from unittest.mock import patch, MagicMock
from api.file_info import get_file_info
from helpers import files

class TestApiFileInfo(unittest.TestCase):
    def test_get_file_info_valid_path(self):
        # Create a dummy file to test
        import os
        test_file = files.get_abs_path("usr/uploads/test_file.txt")
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        with open(test_file, 'w') as f:
            f.write("test")

        loop = asyncio.get_event_loop()
        info = loop.run_until_complete(get_file_info("usr/uploads/test_file.txt"))

        self.assertTrue(info["exists"])
        self.assertEqual(info["file_name"], "test_file.txt")

        # Cleanup
        os.remove(test_file)

    def test_get_file_info_invalid_path(self):
        loop = asyncio.get_event_loop()
        with self.assertRaises(ValueError):
            loop.run_until_complete(get_file_info("../../../etc/passwd"))

if __name__ == '__main__':
    unittest.main()
