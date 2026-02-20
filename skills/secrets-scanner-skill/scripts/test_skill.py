#!/usr/bin/env python3
"""
Secrets Scanner Skill - Test Suite
"""

import os
import sys
import json
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from main import SecretsScanner, SecretFinding, calculate_entropy


class TestSecretsScanner(unittest.TestCase):
    """Test cases for SecretsScanner."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.scanner = SecretsScanner(verbose=False)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_file(self, filename: str, content: str) -> str:
        """Create a test file with given content."""
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath
    
    def test_entropy_calculation(self):
        """Test Shannon entropy calculation."""
        # Low entropy string
        low_entropy = "aaaaaaaa"
        self.assertLess(self.scanner.calculate_entropy(low_entropy), 1.0)
        
        # High entropy string
        high_entropy = "AKIAIOSFODNN7EXAMPLE"
        self.assertGreater(self.scanner.calculate_entropy(high_entropy), 3.0)
    
    def test_aws_access_key_detection(self):
        """Test AWS access key detection."""
        content = """
# Configuration
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_REGION = "us-east-1"
"""
        self.create_test_file("config.py", content)
        
        results = self.scanner.scan_directory(self.temp_dir)
        
        types = [f["type"] for f in results["findings"]]
        self.assertIn("aws_access_key", types)
    
    def test_github_token_detection(self):
        """Test GitHub token detection."""
        content = """
const TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx";
"""
        self.create_test_file("auth.js", content)
        
        results = self.scanner.scan_directory(self.temp_dir)
        
        types = [f["type"] for f in results["findings"]]
        self.assertIn("github_token", types)
    
    def test_private_key_detection(self):
        """Test private key detection."""
        content = """
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA0Z3Z9...
-----END RSA PRIVATE KEY-----
"""
        self.create_test_file("key.pem", content)
        
        results = self.scanner.scan_directory(self.temp_dir)
        
        types = [f["type"] for f in results["findings"]]
        self.assertIn("private_key", types)
    
    def test_password_detection(self):
        """Test password detection."""
        content = """
database_password = "SuperSecret123!"
"""
        self.create_test_file("db.py", content)
        
        results = self.scanner.scan_directory(self.temp_dir)
        
        types = [f["type"] for f in results["findings"]]
        self.assertIn("password", types)
    
    def test_jwt_detection(self):
        """Test JWT token detection."""
        content = """
const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U";
"""
        self.create_test_file("token.js", content)
        
        results = self.scanner.scan_directory(self.temp_dir)
        
        types = [f["type"] for f in results["findings"]]
        self.assertIn("jwt_token", types)
    
    def test_slack_token_detection(self):
        """Test Slack token detection."""
        content = """
SLACK_TOKEN = "xoxb-FAKE1234567890-FAKE1234567890-FAKEFAKEFAKEFAKE"
"""
        self.create_test_file("slack.py", content)
        
        results = self.scanner.scan_directory(self.temp_dir)
        
        types = [f["type"] for f in results["findings"]]
        self.assertIn("slack_token", types)
    
    def test_database_url_detection(self):
        """Test database URL detection."""
        content = """
DATABASE_URL = "postgresql://user:password123@localhost:5432/mydb"
"""
        self.create_test_file("config.py", content)
        
        results = self.scanner.scan_directory(self.temp_dir)
        
        types = [f["type"] for f in results["findings"]]
        self.assertIn("database_url", types)
    
    def test_stripe_key_detection(self):
        """Test Stripe key detection."""
        content = """
STRIPE_SECRET_KEY = "sk_live_EXAMPLE_1234567890_TEST_ONLY"
"""
        self.create_test_file("payments.py", content)
        
        results = self.scanner.scan_directory(self.temp_dir)
        
        types = [f["type"] for f in results["findings"]]
        self.assertIn("stripe_key", types)
    
    def test_results_structure(self):
        """Test scan results structure."""
        content = "AWS_ACCESS_KEY = 'AKIAIOSFODNN7EXAMPLE'"
        self.create_test_file("test.py", content)
        
        results = self.scanner.scan_directory(self.temp_dir)
        
        self.assertIn("scan_info", results)
        self.assertIn("findings", results)
        self.assertIn("summary", results)
        
        self.assertIn("target", results["scan_info"])
        self.assertIn("timestamp", results["scan_info"])
        self.assertIn("files_scanned", results["scan_info"])
    
    def test_finding_structure(self):
        """Test finding object structure."""
        content = "password = 'secret123'"
        self.create_test_file("test.py", content)
        
        results = self.scanner.scan_directory(self.temp_dir)
        
        if results["findings"]:
            finding = results["findings"][0]
            required_fields = ["id", "type", "severity", "file", "line", 
                              "column", "match", "context", "entropy"]
            for field in required_fields:
                self.assertIn(field, finding)
    
    def test_excluded_directories(self):
        """Test that excluded directories are skipped."""
        # Create file in excluded directory
        excluded_dir = os.path.join(self.temp_dir, "node_modules")
        os.makedirs(excluded_dir)
        
        with open(os.path.join(excluded_dir, "secret.js"), 'w') as f:
            f.write('AWS_KEY = "AKIAIOSFODNN7EXAMPLE"')
        
        results = self.scanner.scan_directory(self.temp_dir)
        
        # Should not find the secret in node_modules
        for finding in results["findings"]:
            self.assertNotIn("node_modules", finding["file"])


class TestEdgeCases(unittest.TestCase):
    """Test edge cases."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.scanner = SecretsScanner(verbose=False)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_nonexistent_path(self):
        """Test handling of non-existent path."""
        with self.assertRaises(FileNotFoundError):
            self.scanner.scan_directory("/nonexistent/path/12345")
    
    def test_empty_directory(self):
        """Test scanning empty directory."""
        results = self.scanner.scan_directory(self.temp_dir)
        
        self.assertEqual(results["scan_info"]["files_scanned"], 0)
        self.assertEqual(len(results["findings"]), 0)
    
    def test_single_file_scan(self):
        """Test scanning single file."""
        filepath = os.path.join(self.temp_dir, "single.py")
        with open(filepath, 'w') as f:
            f.write('password = "secret123456"')
        
        results = self.scanner.scan_directory(filepath)
        
        self.assertEqual(results["scan_info"]["files_scanned"], 1)
        self.assertGreater(len(results["findings"]), 0)
    
    def test_include_patterns(self):
        """Test include pattern filtering."""
        # Create Python and JS files
        with open(os.path.join(self.temp_dir, "test.py"), 'w') as f:
            f.write('password = "secret"')
        
        with open(os.path.join(self.temp_dir, "test.js"), 'w') as f:
            f.write('const password = "secret"')
        
        # Scan only Python files
        results = self.scanner.scan_directory(self.temp_dir, include_patterns=["*.py"])
        
        for finding in results["findings"]:
            self.assertTrue(finding["file"].endswith(".py"))


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestSecretsScanner))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
