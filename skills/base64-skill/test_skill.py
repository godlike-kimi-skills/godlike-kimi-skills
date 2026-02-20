#!/usr/bin/env python3
"""
Tests for Base64 Skill
"""

import unittest
import os
import tempfile
from skills.base64_skill.main import Base64Skill


class TestBase64Skill(unittest.TestCase):
    """Test cases for Base64Skill"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.skill = Base64Skill()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test files"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_encode_text(self):
        """Test text encoding"""
        result = self.skill.encode_text("Hello World")
        self.assertEqual(result, "SGVsbG8gV29ybGQ=")
    
    def test_encode_text_bytes(self):
        """Test bytes encoding"""
        result = self.skill.encode_text(b"Hello World")
        self.assertEqual(result, "SGVsbG8gV29ybGQ=")
    
    def test_decode_text(self):
        """Test text decoding"""
        result = self.skill.decode_text("SGVsbG8gV29ybGQ=")
        self.assertEqual(result, "Hello World")
    
    def test_decode_text_unicode(self):
        """Test unicode text decoding"""
        original = "Hello 你好 🌍"
        encoded = self.skill.encode_text(original)
        decoded = self.skill.decode_text(encoded)
        self.assertEqual(decoded, original)
    
    def test_encode_decode_roundtrip(self):
        """Test encode/decode roundtrip"""
        original = "Test message with special chars: !@#$%"
        encoded = self.skill.encode_text(original)
        decoded = self.skill.decode_text(encoded)
        self.assertEqual(decoded, original)
    
    def test_encode_url_safe(self):
        """Test URL-safe encoding"""
        result = self.skill.encode_url_safe("Hello World!")
        # URL-safe should not have + or / or =
        self.assertNotIn('+', result)
        self.assertNotIn('/', result)
        self.assertNotIn('=', result)
    
    def test_decode_url_safe(self):
        """Test URL-safe decoding"""
        original = "Hello World!"
        encoded = self.skill.encode_url_safe(original)
        decoded = self.skill.decode_url_safe(encoded)
        self.assertEqual(decoded, original)
    
    def test_encode_bytes(self):
        """Test raw bytes encoding"""
        data = b"\x00\x01\x02\x03"
        result = self.skill.encode_bytes(data)
        self.assertIsInstance(result, bytes)
    
    def test_decode_bytes(self):
        """Test raw bytes decoding"""
        original = b"\x00\x01\x02\x03"
        encoded = self.skill.encode_bytes(original)
        decoded = self.skill.decode_bytes(encoded)
        self.assertEqual(decoded, original)
    
    def test_validate_valid(self):
        """Test validation (valid)"""
        result = self.skill.validate("SGVsbG8gV29ybGQ=")
        self.assertTrue(result)
    
    def test_validate_invalid(self):
        """Test validation (invalid)"""
        result = self.skill.validate("NotValid!!!")
        self.assertFalse(result)
    
    def test_validate_with_whitespace(self):
        """Test validation with whitespace"""
        result = self.skill.validate("  SGVsbG8gV29ybGQ=  ")
        self.assertTrue(result)
    
    def test_is_valid_with_error(self):
        """Test is_valid with error message"""
        is_valid, error = self.skill.is_valid("Invalid!!!")
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
    
    def test_get_info(self):
        """Test get_info"""
        info = self.skill.get_info("SGVsbG8gV29ybGQ=")
        
        self.assertIn('valid', info)
        self.assertIn('length_chars', info)
        self.assertIn('length_bytes', info)
        self.assertTrue(info['valid'])
    
    def test_get_info_data_uri(self):
        """Test get_info with data URI"""
        data_uri = "data:text/plain;base64,SGVsbG8="
        info = self.skill.get_info(data_uri)
        
        self.assertTrue(info['is_data_uri'])
    
    def test_encode_with_line_breaks(self):
        """Test encoding with line breaks"""
        data = "A" * 100
        result = self.skill.encode_with_line_breaks(data, line_length=20)
        
        lines = result.split('\n')
        self.assertGreater(len(lines), 1)
    
    def test_strip_padding(self):
        """Test padding removal"""
        result = self.skill.strip_padding("SGVsbG8gV29ybGQ=")
        self.assertNotIn('=', result)
    
    def test_add_padding(self):
        """Test padding addition"""
        unpadded = "SGVsbG8gV29ybGQ"
        result = self.skill.add_padding(unpadded)
        self.assertEqual(result, "SGVsbG8gV29ybGQ=")
    
    def test_encode_file(self):
        """Test file encoding"""
        filepath = os.path.join(self.temp_dir, "test.txt")
        content = "Hello World"
        with open(filepath, 'w') as f:
            f.write(content)
        
        result = self.skill.encode_file(filepath)
        
        # Should match text encoding
        expected = self.skill.encode_text(content)
        self.assertEqual(result, expected)
    
    def test_decode_file(self):
        """Test file decoding"""
        original = "Test content for file"
        encoded = self.skill.encode_text(original)
        
        output_path = os.path.join(self.temp_dir, "output.txt")
        self.skill.decode_file(encoded, output_path)
        
        with open(output_path, 'r') as f:
            result = f.read()
        
        self.assertEqual(result, original)
    
    def test_file_not_found(self):
        """Test file not found handling"""
        with self.assertRaises(FileNotFoundError):
            self.skill.encode_file("/nonexistent/file.txt")
    
    def test_invalid_base64_decode(self):
        """Test invalid Base64 decode handling"""
        with self.assertRaises(ValueError):
            self.skill.decode_text("NotValid!!!")


if __name__ == '__main__':
    unittest.main()
