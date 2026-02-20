#!/usr/bin/env python3
"""
Security Audit Skill - Test Suite
"""

import os
import sys
import json
import tempfile
import unittest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from main import SecurityAuditor, Vulnerability, Severity


class TestSecurityAuditor(unittest.TestCase):
    """Test cases for SecurityAuditor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
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
    
    def test_python_sql_injection(self):
        """Test detection of Python SQL injection."""
        code = '''
import sqlite3

def get_user(username):
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE name = '%s'" % username)
    return cursor.fetchone()
'''
        self.create_test_file("test_sql.py", code)
        
        auditor = SecurityAuditor("python")
        results = auditor.audit(self.temp_dir)
        
        vuln_types = [v["type"] for v in results["vulnerabilities"]]
        self.assertIn("sql_injection", vuln_types)
    
    def test_python_hardcoded_secret(self):
        """Test detection of hardcoded secrets."""
        code = '''
API_KEY = "sk-1234567890abcdef"
PASSWORD = "SuperSecret123!"
'''
        self.create_test_file("test_secrets.py", code)
        
        auditor = SecurityAuditor("python")
        results = auditor.audit(self.temp_dir)
        
        vuln_types = [v["type"] for v in results["vulnerabilities"]]
        self.assertIn("hardcoded_secret", vuln_types)
    
    def test_javascript_xss(self):
        """Test detection of JavaScript XSS."""
        code = '''
function displayUserInput(input) {
    document.getElementById('output').innerHTML = '<div>' + input + '</div>';
}
'''
        self.create_test_file("test_xss.js", code)
        
        auditor = SecurityAuditor("javascript")
        results = auditor.audit(self.temp_dir)
        
        vuln_types = [v["type"] for v in results["vulnerabilities"]]
        self.assertIn("xss_vulnerability", vuln_types)
    
    def test_javascript_eval(self):
        """Test detection of dangerous eval usage."""
        code = '''
function processData(data) {
    return eval('(' + data + ')');
}
'''
        self.create_test_file("test_eval.js", code)
        
        auditor = SecurityAuditor("javascript")
        results = auditor.audit(self.temp_dir)
        
        vuln_types = [v["type"] for v in results["vulnerabilities"]]
        self.assertIn("eval_usage", vuln_types)
    
    def test_java_sql_injection(self):
        """Test detection of Java SQL injection."""
        code = '''
import java.sql.*;

public class UserDAO {
    public User getUser(String username) {
        Statement stmt = connection.createStatement();
        ResultSet rs = stmt.executeQuery("SELECT * FROM users WHERE name = '" + username + "'");
        // ...
    }
}
'''
        self.create_test_file("UserDAO.java", code)
        
        auditor = SecurityAuditor("java")
        results = auditor.audit(self.temp_dir)
        
        vuln_types = [v["type"] for v in results["vulnerabilities"]]
        self.assertIn("sql_injection", vuln_types)
    
    def test_report_generation(self):
        """Test JSON report generation."""
        code = 'API_KEY = "secret123"'
        self.create_test_file("test_report.py", code)
        
        auditor = SecurityAuditor("python")
        results = auditor.audit(self.temp_dir)
        
        # Verify report structure
        self.assertIn("scan_info", results)
        self.assertIn("vulnerabilities", results)
        self.assertIn("summary", results)
        self.assertIn("risk_score", results)
        
        # Verify scan_info fields
        self.assertIn("language", results["scan_info"])
        self.assertIn("timestamp", results["scan_info"])
        self.assertIn("total_files", results["scan_info"])
        
        # Verify summary counts
        summary = results["summary"]
        self.assertIn("CRITICAL", summary)
        self.assertIn("HIGH", summary)
        self.assertIn("MEDIUM", summary)
        self.assertIn("LOW", summary)
        self.assertIn("INFO", summary)
    
    def test_risk_score_calculation(self):
        """Test risk score calculation."""
        code = '''
import pickle
import os

data = pickle.loads(user_input)
os.system("ls " + user_input)
'''
        self.create_test_file("test_risk.py", code)
        
        auditor = SecurityAuditor("python")
        results = auditor.audit(self.temp_dir)
        
        self.assertGreater(results["risk_score"], 0)
        self.assertLessEqual(results["risk_score"], 100)
    
    def test_empty_directory(self):
        """Test scanning empty directory."""
        auditor = SecurityAuditor("python")
        results = auditor.audit(self.temp_dir)
        
        self.assertEqual(results["scan_info"]["total_files"], 0)
        self.assertEqual(len(results["vulnerabilities"]), 0)
        self.assertEqual(results["risk_score"], 0.0)
    
    def test_single_file_scan(self):
        """Test scanning single file."""
        code = 'password = "secret123456"'
        filepath = self.create_test_file("single.py", code)
        
        auditor = SecurityAuditor("python")
        results = auditor.audit(filepath)
        
        self.assertEqual(results["scan_info"]["total_files"], 1)
        self.assertGreater(len(results["vulnerabilities"]), 0)
    
    def test_vulnerability_structure(self):
        """Test vulnerability object structure."""
        code = 'eval("alert(1)")'
        self.create_test_file("test_struct.js", code)
        
        auditor = SecurityAuditor("javascript")
        results = auditor.audit(self.temp_dir)
        
        if results["vulnerabilities"]:
            vuln = results["vulnerabilities"][0]
            required_fields = ["id", "severity", "type", "file", "line", 
                              "column", "description", "recommendation", "code_snippet"]
            for field in required_fields:
                self.assertIn(field, vuln)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def test_nonexistent_path(self):
        """Test handling of non-existent path."""
        auditor = SecurityAuditor("python")
        with self.assertRaises(FileNotFoundError):
            auditor.audit("/nonexistent/path/12345")
    
    def test_invalid_language(self):
        """Test handling of unsupported language."""
        auditor = SecurityAuditor("ruby")
        results = auditor.audit(tempfile.mkdtemp())
        self.assertEqual(len(results["vulnerabilities"]), 0)


def run_tests():
    """Run all tests and return results."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityAuditor))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
