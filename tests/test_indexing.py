import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import backend.indexing

class TestIndexing(unittest.TestCase):
    def test_import(self):
        self.assertIsNotNone(backend.indexing)

if __name__ == '__main__':
    unittest.main()
