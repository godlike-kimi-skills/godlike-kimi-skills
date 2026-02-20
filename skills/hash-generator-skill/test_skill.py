#!/usr/bin/env python3
"""
Tests for Hash Generator Skill
"""

import unittest
import os
import tempfile
from skills.hash_generator_skill.main import HashGeneratorSkill


class TestHashGeneratorSkill(unittest.TestCase):
    """Test cases for HashGeneratorSkill"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.skill = HashGeneratorSkill()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test files"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_hash_string_md5(self):
        """Test MD5 hashing"""
        result = self.skill.hash_string("Hello World", "md5")
        self.assertEqual(len(result), 32)
        self.assertEqual(result.lower(), "b10a8db164e0754105b7a99be72e3fe5")
    
    def test_hash_string_sha256(self):
        """Test SHA-256 hashing"""
        result = self.skill.hash_string("Hello World", "sha256")
        self.assertEqual(len(result), 64)
        # Known SHA-256 hash for "Hello World"
        expected = "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e"
        self.assertEqual(result.lower(), expected)
    
    def test_hash_string_bytes(self):
        """Test hashing bytes"""
        result_str = self.skill.hash_string("test", "sha256")
        result_bytes = self.skill.hash_string(b"test", "sha256")
        self.assertEqual(result_str, result_bytes)
    
    def test_hash_file(self):
        """Test file hashing"""
        filepath = os.path.join(self.temp_dir, "test.txt")
        with open(filepath, 'w') as f:
            f.write("Hello World")
        
        result = self.skill.hash_file(filepath, "sha256")
        self.assertEqual(len(result), 64)
        
        # Should match string hash
        string_hash = self.skill.hash_string("Hello World", "sha256")
        self.assertEqual(result, string_hash)
    
    def test_hmac_string(self):
        """Test HMAC generation"""
        result = self.skill.hmac_string("message", "secret", "sha256")
        self.assertEqual(len(result), 64)
        
        # Same input should produce same output
        result2 = self.skill.hmac_string("message", "secret", "sha256")
        self.assertEqual(result, result2)
        
        # Different key should produce different output
        result3 = self.skill.hmac_string("message", "different", "sha256")
        self.assertNotEqual(result, result3)
    
    def test_compare_hashes_equal(self):
        """Test hash comparison (equal)"""
        hash1 = self.skill.hash_string("test", "sha256")
        hash2 = self.skill.hash_string("test", "sha256")
        result = self.skill.compare_hashes(hash1, hash2)
        self.assertTrue(result)
    
    def test_compare_hashes_different(self):
        """Test hash comparison (different)"""
        hash1 = self.skill.hash_string("test1", "sha256")
        hash2 = self.skill.hash_string("test2", "sha256")
        result = self.skill.compare_hashes(hash1, hash2)
        self.assertFalse(result)
    
    def test_compare_hashes_case_insensitive(self):
        """Test hash comparison is case insensitive"""
        hash1 = self.skill.hash_string("test", "sha256").upper()
        hash2 = self.skill.hash_string("test", "sha256").lower()
        result = self.skill.compare_hashes(hash1, hash2)
        self.assertTrue(result)
    
    def test_verify_string_valid(self):
        """Test string verification (valid)"""
        expected = self.skill.hash_string("test", "sha256")
        result = self.skill.verify_string("test", expected, "sha256")
        self.assertTrue(result)
    
    def test_verify_string_invalid(self):
        """Test string verification (invalid)"""
        result = self.skill.verify_string("test", "wrong_hash", "sha256")
        self.assertFalse(result)
    
    def test_verify_file_valid(self):
        """Test file verification (valid)"""
        filepath = os.path.join(self.temp_dir, "test.txt")
        with open(filepath, 'w') as f:
            f.write("Hello World")
        
        expected = self.skill.hash_file(filepath, "sha256")
        result = self.skill.verify_file(filepath, expected, "sha256")
        self.assertTrue(result)
    
    def test_batch_hash_files(self):
        """Test batch file hashing"""
        files = []
        for i in range(3):
            filepath = os.path.join(self.temp_dir, f"test{i}.txt")
            with open(filepath, 'w') as f:
                f.write(f"content{i}")
            files.append(filepath)
        
        results = self.skill.batch_hash_files(files, "sha256")
        
        self.assertEqual(len(results), 3)
        for f in files:
            self.assertIn(f, results)
            self.assertEqual(len(results[f]), 64)
    
    def test_get_algorithm_info(self):
        """Test algorithm info retrieval"""
        info = self.skill.get_algorithm_info("sha256")
        
        self.assertTrue(info['supported'])
        self.assertTrue(info['secure'])
        self.assertFalse(info['insecure'])
        self.assertEqual(info['digest_size'], 64)
    
    def test_get_algorithm_info_insecure(self):
        """Test algorithm info for insecure algorithms"""
        info = self.skill.get_algorithm_info("md5")
        
        self.assertTrue(info['supported'])
        self.assertFalse(info['secure'])
        self.assertTrue(info['insecure'])
    
    def test_list_algorithms(self):
        """Test algorithm listing"""
        algos = self.skill.list_algorithms()
        
        self.assertIn("md5", algos)
        self.assertIn("sha256", algos)
        self.assertIn("sha512", algos)
    
    def test_unsupported_algorithm(self):
        """Test unsupported algorithm handling"""
        with self.assertRaises(ValueError):
            self.skill.hash_string("test", "invalid_algo")


if __name__ == '__main__':
    unittest.main()
