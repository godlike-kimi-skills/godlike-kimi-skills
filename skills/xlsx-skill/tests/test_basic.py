#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basic tests for Excel Processor
Author: godlike-kimi
License: MIT
"""

import os
import sys
import json
import tempfile
import unittest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import ExcelProcessor


class TestExcelProcessor(unittest.TestCase):
    """Test cases for ExcelProcessor class"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.xlsx")
        self.processor = ExcelProcessor()

    def tearDown(self):
        """Clean up test files"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        os.rmdir(self.temp_dir)

    def test_create_workbook(self):
        """Test creating a new workbook"""
        self.assertIsNotNone(self.processor.workbook)
        self.assertEqual(len(self.processor.workbook.sheetnames), 1)

    def test_write_and_read_dict_data(self):
        """Test writing and reading dictionary data"""
        test_data = [
            {"name": "John", "age": 30, "city": "New York"},
            {"name": "Jane", "age": 25, "city": "London"},
            {"name": "Bob", "age": 35, "city": "Paris"}
        ]

        # Write data
        self.processor.write(test_data, "Sheet1", headers=True)
        self.processor.save(self.test_file)

        # Read data back
        processor2 = ExcelProcessor(self.test_file)
        result = processor2.read("Sheet1", headers=True)

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["name"], "John")
        self.assertEqual(result[0]["age"], 30)
        self.assertEqual(result[1]["name"], "Jane")

    def test_write_and_read_list_data(self):
        """Test writing and reading list data"""
        test_data = [
            ["Name", "Age", "City"],
            ["John", 30, "New York"],
            ["Jane", 25, "London"]
        ]

        # Write data with headers
        self.processor.write(test_data, "Sheet1", headers=False)
        self.processor.save(self.test_file)

        # Read without headers
        processor2 = ExcelProcessor(self.test_file)
        result = processor2.read("Sheet1", headers=False)

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], ["Name", "Age", "City"])
        self.assertEqual(result[1], ["John", 30, "New York"])

    def test_append_data(self):
        """Test appending data to existing sheet"""
        # Initial data
        initial_data = [{"name": "John", "age": 30}]
        self.processor.write(initial_data, "Sheet1")

        # Append data
        self.processor.append({"name": "Jane", "age": 25}, "Sheet1")
        self.processor.save(self.test_file)

        # Verify
        processor2 = ExcelProcessor(self.test_file)
        result = processor2.read("Sheet1")

        self.assertEqual(len(result), 2)
        self.assertEqual(result[1]["name"], "Jane")

    def test_add_formula(self):
        """Test adding formulas to cells"""
        # Write some numbers
        test_data = [
            {"value": 10},
            {"value": 20},
            {"value": 30}
        ]
        self.processor.write(test_data, "Sheet1")

        # Add formula
        self.processor.add_formula("B5", "=SUM(A2:A4)", "Sheet1")
        self.processor.save(self.test_file)

        # Verify file was created
        self.assertTrue(os.path.exists(self.test_file))

    def test_format_cells(self):
        """Test cell formatting"""
        # Write data
        test_data = [{"col1": "Test", "col2": 123}]
        self.processor.write(test_data, "Sheet1")

        # Apply formatting
        font = {"bold": True, "size": 14}
        fill = {"color": "FFFF00"}
        alignment = {"horizontal": "center"}

        self.processor.format_cells("A1:B1", "Sheet1", font, fill, alignment)
        self.processor.save(self.test_file)

        # Verify file was created
        self.assertTrue(os.path.exists(self.test_file))

    def test_multiple_sheets(self):
        """Test working with multiple sheets"""
        # Write to different sheets
        self.processor.write([{"data": "Sheet1 Data"}], "Sheet1")
        self.processor.write([{"data": "Sheet2 Data"}], "Sheet2")
        self.processor.save(self.test_file)

        # Verify both sheets exist
        self.assertEqual(len(self.processor.workbook.sheetnames), 2)
        self.assertIn("Sheet1", self.processor.workbook.sheetnames)
        self.assertIn("Sheet2", self.processor.workbook.sheetnames)

    def test_custom_headers(self):
        """Test custom headers"""
        test_data = [
            {"n": "John", "a": 30},
            {"n": "Jane", "a": 25}
        ]

        custom_headers = ["Name", "Age"]
        self.processor.write(test_data, "Sheet1", headers=custom_headers)
        self.processor.save(self.test_file)

        processor2 = ExcelProcessor(self.test_file)
        result = processor2.read("Sheet1")

        self.assertEqual(len(result), 2)

    def test_empty_data(self):
        """Test handling empty data"""
        self.processor.write([], "Sheet1")
        self.processor.save(self.test_file)

        processor2 = ExcelProcessor(self.test_file)
        result = processor2.read("Sheet1")

        self.assertEqual(len(result), 0)

    def test_special_characters(self):
        """Test handling special characters"""
        test_data = [
            {"name": "测试中文", "value": 100},
            {"name": "日本語テスト", "value": 200},
            {"name": "Special!@#$%", "value": 300}
        ]

        self.processor.write(test_data, "Sheet1")
        self.processor.save(self.test_file)

        processor2 = ExcelProcessor(self.test_file)
        result = processor2.read("Sheet1")

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["name"], "测试中文")
        self.assertEqual(result[1]["name"], "日本語テスト")


class TestCommandLine(unittest.TestCase):
    """Test cases for command line interface"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.xlsx")

    def tearDown(self):
        """Clean up test files"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists(os.path.join(self.temp_dir, "output.xlsx")):
            os.remove(os.path.join(self.temp_dir, "output.xlsx"))
        os.rmdir(self.temp_dir)

    def test_cli_write_and_read(self):
        """Test CLI write and read operations"""
        import subprocess

        # Write data via CLI
        test_data = json.dumps([{"name": "Test", "value": 123}])
        result = subprocess.run(
            [sys.executable, "-m", "main", "write", 
             "--input", self.test_file, 
             "--data", test_data],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )
        self.assertEqual(result.returncode, 0)
        self.assertTrue(os.path.exists(self.test_file))

        # Read data via CLI
        result = subprocess.run(
            [sys.executable, "-m", "main", "read", 
             "--input", self.test_file],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent)
        )
        self.assertEqual(result.returncode, 0)
        
        # Parse output
        data = json.loads(result.stdout)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Test")


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestExcelProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestCommandLine))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
