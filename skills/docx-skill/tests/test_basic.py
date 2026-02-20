#!/usr/bin/env python3
"""基础测试"""
import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestDocxProcessor(unittest.TestCase):
    def test_import(self):
        try:
            from main import DocxProcessor
            self.assertTrue(True)
        except ImportError:
            self.assertTrue(False, "Cannot import DocxProcessor")

if __name__ == "__main__":
    unittest.main()
