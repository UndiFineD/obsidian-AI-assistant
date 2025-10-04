import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import backend.modelmanager

class TestModelManager(unittest.TestCase):
    def test_import(self):
        self.assertIsNotNone(backend.modelmanager)

if __name__ == '__main__':
    unittest.main()
