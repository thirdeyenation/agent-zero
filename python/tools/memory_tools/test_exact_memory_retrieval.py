import unittest
import sys
import os
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from memory_tools.exact_memory_retrieval import exact_memory_retrieval
from a0.memory_tool import memory_load

class TestExactMemoryRetrieval(unittest.TestCase):

    def test_successful_retrieval(self):
        mock_memory_load = MagicMock(return_value='{\n    "area": "main",\n    "id": "test_id",\n    "timestamp": "2025-01-23 00:00:00",\n    "Content": "This is a test memory."\n}')
        memory_load = mock_memory_load
        result = exact_memory_retrieval('test_id')
        self.assertIn("This is a test memory.", result)

    def test_memory_not_found(self):
        mock_memory_load = MagicMock(return_value='{\n    "memory": "No memories found for specified query: test_id"\n}')
        memory_load = mock_memory_load
        result = exact_memory_retrieval('test_id')
        self.assertIn("Error: Memory not found for specified ID: test_id", result)

    def test_invalid_memory_id(self):
        result = exact_memory_retrieval(None)
        self.assertIn("Error: An error occurred during memory retrieval", result)

if __name__ == '__main__':
    unittest.main()
