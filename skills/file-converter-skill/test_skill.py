#!/usr/bin/env python3
"""
Tests for File Converter Skill
"""

import unittest
import os
import tempfile
import json
from skills.file_converter_skill.main import FileConverterSkill


class TestFileConverterSkill(unittest.TestCase):
    """Test cases for FileConverterSkill"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.skill = FileConverterSkill()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test files"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_test_csv(self, filename, data):
        """Helper to create test CSV file"""
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            import csv
            writer = csv.writer(f)
            writer.writerows(data)
        return filepath
    
    def _create_test_json(self, filename, data):
        """Helper to create test JSON file"""
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        return filepath
    
    def test_convert_csv_to_json(self):
        """Test CSV to JSON conversion"""
        csv_data = [
            ['name', 'age', 'city'],
            ['Alice', '30', 'New York'],
            ['Bob', '25', 'London'],
        ]
        csv_path = self._create_test_csv('test.csv', csv_data)
        json_path = os.path.join(self.temp_dir, 'test.json')
        
        result = self.skill.convert_csv_to_json(csv_path, json_path)
        
        self.assertTrue(os.path.exists(result))
        with open(result, 'r') as f:
            data = json.load(f)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['name'], 'Alice')
    
    def test_convert_json_to_csv(self):
        """Test JSON to CSV conversion"""
        json_data = [
            {'name': 'Alice', 'age': 30},
            {'name': 'Bob', 'age': 25},
        ]
        json_path = self._create_test_json('test.json', json_data)
        csv_path = os.path.join(self.temp_dir, 'test.csv')
        
        result = self.skill.convert_json_to_csv(json_path, csv_path)
        
        self.assertTrue(os.path.exists(result))
        with open(result, 'r', newline='') as f:
            import csv
            reader = csv.DictReader(f)
            rows = list(reader)
        self.assertEqual(len(rows), 2)
    
    def test_validate_json_valid(self):
        """Test JSON validation (valid)"""
        json_path = self._create_test_json('valid.json', {'key': 'value'})
        result = self.skill.validate_json(json_path)
        self.assertTrue(result)
    
    def test_validate_json_invalid(self):
        """Test JSON validation (invalid)"""
        filepath = os.path.join(self.temp_dir, 'invalid.json')
        with open(filepath, 'w') as f:
            f.write('{"key": invalid}')
        
        result = self.skill.validate_json(filepath)
        self.assertFalse(result)
    
    def test_validate_xml_valid(self):
        """Test XML validation (valid)"""
        filepath = os.path.join(self.temp_dir, 'valid.xml')
        with open(filepath, 'w') as f:
            f.write('<root><item>value</item></root>')
        
        result = self.skill.validate_xml(filepath)
        self.assertTrue(result)
    
    def test_validate_xml_invalid(self):
        """Test XML validation (invalid)"""
        filepath = os.path.join(self.temp_dir, 'invalid.xml')
        with open(filepath, 'w') as f:
            f.write('<root><unclosed>')
        
        result = self.skill.validate_xml(filepath)
        self.assertFalse(result)
    
    def test_detect_encoding_utf8(self):
        """Test encoding detection (UTF-8)"""
        filepath = os.path.join(self.temp_dir, 'utf8.txt')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('Hello World 你好')
        
        detected = self.skill._detect_encoding(filepath)
        self.assertIn(detected.lower(), ['utf-8', 'utf-8-sig', 'ascii'])
    
    def test_convert_encoding(self):
        """Test encoding conversion"""
        # Create file with specific encoding
        filepath = os.path.join(self.temp_dir, 'gbk.txt')
        with open(filepath, 'w', encoding='gbk') as f:
            f.write('中文内容')
        
        output = os.path.join(self.temp_dir, 'utf8.txt')
        result = self.skill.convert_encoding(filepath, output, to_encoding='utf-8')
        
        self.assertTrue(os.path.exists(result))
        with open(result, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, '中文内容')
    
    def test_merge_csv_files(self):
        """Test CSV file merging"""
        csv1 = self._create_test_csv('file1.csv', [
            ['name', 'value'],
            ['A', '1'],
        ])
        csv2 = self._create_test_csv('file2.csv', [
            ['name', 'value'],
            ['B', '2'],
        ])
        
        output = os.path.join(self.temp_dir, 'merged.csv')
        result = self.skill.merge_csv_files([csv1, csv2], output)
        
        self.assertTrue(os.path.exists(result))
        with open(result, 'r', newline='') as f:
            import csv
            reader = csv.DictReader(f)
            rows = list(reader)
        self.assertEqual(len(rows), 2)


if __name__ == '__main__':
    unittest.main()
