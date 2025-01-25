import unittest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../memory_tools')))
from memory_tools.test_exact_memory_retrieval import TestExactMemoryRetrieval

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestExactMemoryRetrieval))
    runner = unittest.TextTestRunner()
    runner.run(suite)
