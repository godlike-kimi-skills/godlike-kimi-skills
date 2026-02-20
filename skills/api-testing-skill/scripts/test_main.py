#!/usr/bin/env python3
"""Tests for API Testing Skill."""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from main import (
    APITester, TestCase, TestResult,
    parse_env_vars
)


class TestTestResult(unittest.TestCase):
    """Test TestResult dataclass."""
    
    def test_creation(self):
        """Test TestResult creation."""
        result = TestResult(
            name="Test API",
            passed=True,
            duration_ms=100.5
        )
        self.assertEqual(result.name, "Test API")
        self.assertTrue(result.passed)
        self.assertEqual(result.duration_ms, 100.5)


class TestTestCase(unittest.TestCase):
    """Test TestCase dataclass."""
    
    def test_creation(self):
        """Test TestCase creation."""
        case = TestCase(
            name="Get User",
            request={"method": "GET", "url": "/users/1"},
            assertions=[{"type": "status_code", "expected": 200}]
        )
        self.assertEqual(case.name, "Get User")
        self.assertFalse(case.skip)


class TestAPITester(unittest.TestCase):
    """Test APITester functionality."""
    
    def setUp(self):
        """Set up tester."""
        self.tester = APITester()
    
    def test_substitute_variables(self):
        """Test variable substitution."""
        self.tester.env_vars = {"BASE_URL": "https://api.example.com"}
        
        result = self.tester._substitute_variables("${BASE_URL}/users")
        self.assertEqual(result, "https://api.example.com/users")
    
    def test_substitute_variables_with_default(self):
        """Test variable substitution with default."""
        result = self.tester._substitute_variables("${MISSING:default}")
        self.assertEqual(result, "default")
    
    def test_substitute_variables_nested(self):
        """Test variable substitution in nested structures."""
        self.tester.env_vars = {"TOKEN": "abc123"}
        
        data = {
            "headers": {"Authorization": "Bearer ${TOKEN}"},
            "url": "${BASE_URL:https://default.com}/api"
        }
        result = self.tester._substitute_variables(data)
        
        self.assertEqual(result["headers"]["Authorization"], "Bearer abc123")
        self.assertEqual(result["url"], "https://default.com/api")
    
    def test_extract_json_value(self):
        """Test JSON value extraction."""
        data = {
            "user": {
                "name": "John",
                "email": "john@example.com",
                "roles": ["admin", "user"]
            },
            "count": 5
        }
        
        self.assertEqual(
            self.tester._extract_json_value(data, "$.user.name"),
            "John"
        )
        self.assertEqual(
            self.tester._extract_json_value(data, "$.user.roles[0]"),
            "admin"
        )
        self.assertEqual(
            self.tester._extract_json_value(data, "$.count"),
            5
        )
    
    @patch('main.requests.Session.request')
    def test_run_test_status_code_assertion(self, mock_request):
        """Test running test with status code assertion."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.text = '{"id": 1}'
        mock_response.json.return_value = {"id": 1}
        mock_response.elapsed.total_seconds.return_value = 0.1
        mock_request.return_value = mock_response
        
        test_case = TestCase(
            name="Get User",
            request={"method": "GET", "url": "https://api.example.com/users/1"},
            assertions=[{"type": "status_code", "expected": 200}]
        )
        
        result = self.tester.run_test(test_case)
        
        self.assertTrue(result.passed)
        self.assertEqual(len(result.assertions), 1)
        self.assertTrue(result.assertions[0]['passed'])
    
    @patch('main.requests.Session.request')
    def test_run_test_json_path_assertion(self, mock_request):
        """Test running test with JSON path assertion."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.text = '{"user": {"name": "John"}}'
        mock_response.json.return_value = {"user": {"name": "John"}}
        mock_response.elapsed.total_seconds.return_value = 0.1
        mock_request.return_value = mock_response
        
        test_case = TestCase(
            name="Get User",
            request={"method": "GET", "url": "https://api.example.com/users/1"},
            assertions=[{"type": "json_path", "path": "$.user.name", "expected": "John"}]
        )
        
        result = self.tester.run_test(test_case)
        
        self.assertTrue(result.passed)
    
    @patch('main.requests.Session.request')
    def test_run_test_header_assertion(self, mock_request):
        """Test running test with header assertion."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.text = '{}'
        mock_response.json.return_value = {}
        mock_response.elapsed.total_seconds.return_value = 0.1
        mock_request.return_value = mock_response
        
        test_case = TestCase(
            name="Get User",
            request={"method": "GET", "url": "https://api.example.com/users/1"},
            assertions=[{"type": "header", "name": "Content-Type", "expected": "application/json"}]
        )
        
        result = self.tester.run_test(test_case)
        
        self.assertTrue(result.passed)
    
    @patch('main.requests.Session.request')
    def test_run_test_body_contains_assertion(self, mock_request):
        """Test running test with body contains assertion."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.text = '<html><body>Welcome</body></html>'
        mock_response.elapsed.total_seconds.return_value = 0.1
        mock_request.return_value = mock_response
        
        test_case = TestCase(
            name="Get Page",
            request={"method": "GET", "url": "https://example.com"},
            assertions=[{"type": "body_contains", "expected": "Welcome"}]
        )
        
        result = self.tester.run_test(test_case)
        
        self.assertTrue(result.passed)
    
    @patch('main.requests.Session.request')
    def test_run_test_response_time_assertion(self, mock_request):
        """Test running test with response time assertion."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.text = '{}'
        mock_response.elapsed.total_seconds.return_value = 0.05  # 50ms
        mock_request.return_value = mock_response
        
        test_case = TestCase(
            name="Get User",
            request={"method": "GET", "url": "https://api.example.com/users/1"},
            assertions=[{"type": "response_time", "max_ms": 100}]
        )
        
        result = self.tester.run_test(test_case)
        
        self.assertTrue(result.passed)
    
    @patch('main.requests.Session.request')
    def test_run_test_failed_assertion(self, mock_request):
        """Test running test with failed assertion."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.headers = {}
        mock_response.text = '{"error": "Not found"}'
        mock_response.json.return_value = {"error": "Not found"}
        mock_response.elapsed.total_seconds.return_value = 0.1
        mock_request.return_value = mock_response
        
        test_case = TestCase(
            name="Get User",
            request={"method": "GET", "url": "https://api.example.com/users/1"},
            assertions=[{"type": "status_code", "expected": 200}]
        )
        
        result = self.tester.run_test(test_case)
        
        self.assertFalse(result.passed)
        self.assertEqual(result.assertions[0]['actual'], 404)
        self.assertEqual(result.assertions[0]['expected'], 200)
    
    def test_run_test_skipped(self):
        """Test running skipped test."""
        test_case = TestCase(
            name="Skipped Test",
            request={},
            assertions=[],
            skip=True
        )
        
        result = self.tester.run_test(test_case)
        
        self.assertTrue(result.passed)
        self.assertEqual(result.error_message, "Skipped")
    
    def test_run_from_file_yaml(self):
        """Test running tests from YAML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
name: Test API
request:
  method: GET
  url: https://api.example.com/test
assertions:
  - type: status_code
    expected: 200
""")
            temp_path = f.name
        
        try:
            with patch('main.requests.Session.request') as mock_request:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.headers = {}
                mock_response.text = '{}'
                mock_response.json.return_value = {}
                mock_response.elapsed.total_seconds.return_value = 0.1
                mock_request.return_value = mock_response
                
                results = self.tester.run_from_file(temp_path)
                
                self.assertEqual(len(results), 1)
                self.assertTrue(results[0].passed)
        finally:
            os.unlink(temp_path)
    
    def test_run_from_file_json(self):
        """Test running tests from JSON file."""
        test_data = {
            "tests": [
                {
                    "name": "Test 1",
                    "request": {"method": "GET", "url": "https://api.example.com/test"},
                    "assertions": [{"type": "status_code", "expected": 200}]
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = f.name
        
        try:
            with patch('main.requests.Session.request') as mock_request:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.headers = {}
                mock_response.text = '{}'
                mock_response.json.return_value = {}
                mock_response.elapsed.total_seconds.return_value = 0.1
                mock_request.return_value = mock_response
                
                results = self.tester.run_from_file(temp_path)
                
                self.assertEqual(len(results), 1)
        finally:
            os.unlink(temp_path)
    
    def test_generate_text_report(self):
        """Test text report generation."""
        results = [
            TestResult(name="Test 1", passed=True, duration_ms=100),
            TestResult(name="Test 2", passed=False, duration_ms=50)
        ]
        
        report = self.tester.generate_report(results, 'text')
        
        self.assertIn("Test 1", report)
        self.assertIn("Test 2", report)
        self.assertIn("PASS", report)
        self.assertIn("FAIL", report)
    
    def test_generate_json_report(self):
        """Test JSON report generation."""
        results = [
            TestResult(name="Test 1", passed=True, duration_ms=100)
        ]
        
        report = self.tester.generate_report(results, 'json')
        data = json.loads(report)
        
        self.assertEqual(data['summary']['total'], 1)
        self.assertEqual(data['summary']['passed'], 1)
        self.assertEqual(len(data['results']), 1)
    
    def test_generate_html_report(self):
        """Test HTML report generation."""
        results = [
            TestResult(name="Test 1", passed=True, duration_ms=100)
        ]
        
        report = self.tester.generate_report(results, 'html')
        
        self.assertIn("<html>", report)
        self.assertIn("Test 1", report)
        self.assertIn("PASS", report)


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""
    
    def test_parse_env_vars(self):
        """Test environment variable parsing."""
        env_list = ["KEY1=value1", "KEY2=value2", "INVALID"]
        result = parse_env_vars(env_list)
        
        self.assertEqual(result["KEY1"], "value1")
        self.assertEqual(result["KEY2"], "value2")
        self.assertNotIn("INVALID", result)


class TestVariableExtraction(unittest.TestCase):
    """Test variable extraction from responses."""
    
    def setUp(self):
        """Set up tester."""
        self.tester = APITester()
    
    def test_extract_json_body_variable(self):
        """Test extracting variable from JSON body."""
        mock_response = Mock()
        mock_response.json.return_value = {"id": 123, "token": "abc"}
        
        extractions = [
            {"name": "user_id", "source": "json_body", "path": "$.id"},
            {"name": "auth_token", "source": "json_body", "path": "$.token"}
        ]
        
        self.tester._extract_variables(mock_response, extractions)
        
        self.assertEqual(self.tester.variables["user_id"], 123)
        self.assertEqual(self.tester.variables["auth_token"], "abc")


if __name__ == "__main__":
    unittest.main()
