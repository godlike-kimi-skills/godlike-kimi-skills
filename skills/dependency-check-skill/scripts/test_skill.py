#!/usr/bin/env python3
"""
Dependency Check Skill - Test Suite
"""

import os
import sys
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent))

from main import DependencyChecker, Dependency, Vulnerability


class TestDependencyChecker(unittest.TestCase):
    """Test cases for DependencyChecker."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.checker = DependencyChecker(verbose=False, cache_dir=self.temp_dir)
    
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
    
    def test_parse_requirements(self):
        """Test parsing requirements.txt."""
        content = """
# Comment line
requests==2.25.0
flask>=1.0.0
numpy
pytest==6.2.0
"""
        filepath = self.create_test_file("requirements.txt", content)
        
        deps = self.checker._parse_file(Path(filepath), "requirements")
        
        self.assertEqual(len(deps), 4)
        names = [d.name for d in deps]
        self.assertIn("requests", names)
        self.assertIn("flask", names)
        self.assertIn("numpy", names)
        self.assertIn("pytest", names)
    
    def test_parse_npm(self):
        """Test parsing package.json."""
        content = json.dumps({
            "name": "test-app",
            "dependencies": {
                "express": "^4.17.0",
                "lodash": "~4.17.20"
            },
            "devDependencies": {
                "jest": "^26.0.0"
            }
        })
        filepath = self.create_test_file("package.json", content)
        
        deps = self.checker._parse_file(Path(filepath), "npm")
        
        self.assertEqual(len(deps), 3)
        names = [d.name for d in deps]
        self.assertIn("express", names)
        self.assertIn("lodash", names)
        self.assertIn("jest", names)
    
    def test_parse_pipfile(self):
        """Test parsing Pipfile.lock."""
        content = json.dumps({
            "default": {
                "requests": {"version": "==2.25.1"},
                "flask": {"version": "==1.1.2"}
            }
        })
        filepath = self.create_test_file("Pipfile.lock", content)
        
        deps = self.checker._parse_file(Path(filepath), "pipfile")
        
        self.assertEqual(len(deps), 2)
        names = [d.name for d in deps]
        self.assertIn("requests", names)
        self.assertIn("flask", names)
    
    def test_is_outdated(self):
        """Test version comparison."""
        self.assertTrue(self.checker._is_outdated("1.0.0", "2.0.0"))
        self.assertTrue(self.checker._is_outdated("2.25.0", "2.31.0"))
        self.assertFalse(self.checker._is_outdated("2.0.0", "1.0.0"))
        self.assertFalse(self.checker._is_outdated("2.0.0", "2.0.0"))
        self.assertFalse(self.checker._is_outdated("2.0.0", None))
    
    def test_detect_format(self):
        """Test format auto-detection."""
        test_cases = [
            ("requirements.txt", "requirements"),
            ("requirements-dev.txt", "requirements"),
            ("package.json", "npm"),
            ("Pipfile.lock", "pipfile"),
            ("go.mod", "gomod"),
            ("pom.xml", "maven"),
        ]
        
        for filename, expected in test_cases:
            filepath = os.path.join(self.temp_dir, filename)
            Path(filepath).touch()
            result = self.checker._detect_format(Path(filepath))
            self.assertEqual(result, expected, f"Failed for {filename}")
    
    def test_build_results(self):
        """Test result building."""
        deps = [
            Dependency(name="pkg1", version="1.0.0", vulnerabilities=[]),
            Dependency(
                name="pkg2",
                version="1.0.0",
                vulnerabilities=[
                    Vulnerability(cve_id="CVE-2021-1234", severity="HIGH", description="Test", fixed_in="2.0.0")
                ]
            )
        ]
        
        results = self.checker._build_results("test.txt", "requirements", deps)
        
        self.assertIn("scan_info", results)
        self.assertIn("dependencies", results)
        self.assertIn("summary", results)
        self.assertEqual(results["summary"]["HIGH"], 1)
    
    @patch('main.requests.Session.get')
    def test_get_latest_version_pypi(self, mock_get):
        """Test fetching latest version from PyPI."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"info": {"version": "2.31.0"}}
        mock_get.return_value = mock_response
        
        version = self.checker._get_latest_version("requests", "requirements")
        
        self.assertEqual(version, "2.31.0")
    
    @patch('main.requests.Session.get')
    def test_get_latest_version_npm(self, mock_get):
        """Test fetching latest version from npm registry."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"dist-tags": {"latest": "4.18.2"}}
        mock_get.return_value = mock_response
        
        version = self.checker._get_latest_version("express", "npm")
        
        self.assertEqual(version, "4.18.2")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.checker = DependencyChecker(verbose=False, cache_dir=self.temp_dir)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_nonexistent_file(self):
        """Test handling of non-existent file."""
        with self.assertRaises(FileNotFoundError):
            self.checker.scan_file("/nonexistent/file.txt", "requirements")
    
    def test_unknown_format(self):
        """Test handling of unknown format."""
        filepath = os.path.join(self.temp_dir, "unknown.xyz")
        Path(filepath).touch()
        
        with self.assertRaises(ValueError):
            self.checker._detect_format(Path(filepath))
    
    def test_empty_requirements(self):
        """Test parsing empty requirements file."""
        filepath = os.path.join(self.temp_dir, "empty.txt")
        with open(filepath, 'w') as f:
            f.write("# Only comments\n\n")
        
        deps = self.checker._parse_file(Path(filepath), "requirements")
        self.assertEqual(len(deps), 0)
    
    def test_cve_cache(self):
        """Test CVE caching functionality."""
        # First call should cache
        cache_key = "requirements:pkg:1.0.0"
        vulns = [Vulnerability(cve_id="CVE-2021-1234", severity="HIGH", description="Test", fixed_in="2.0.0")]
        self.checker.cve_cache[cache_key] = [{
            "cve_id": "CVE-2021-1234",
            "severity": "HIGH",
            "description": "Test",
            "fixed_in": "2.0.0",
            "cvss_score": None,
            "references": []
        }]
        
        # Should retrieve from cache
        result = self.checker._check_vulnerabilities("pkg", "1.0.0", "requirements")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].cve_id, "CVE-2021-1234")


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestDependencyChecker))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
