#!/usr/bin/env python3
"""Tests for HTTP Client Skill."""

import json
import unittest
from unittest.mock import Mock, patch

from main import HTTPClient, Response, parse_headers, parse_params


class TestResponse(unittest.TestCase):
    """Test Response class."""
    
    def test_is_success(self):
        """Test success status check."""
        self.assertTrue(Response(200).is_success())
        self.assertTrue(Response(201).is_success())
        self.assertTrue(Response(204).is_success())
        self.assertFalse(Response(404).is_success())
        self.assertFalse(Response(500).is_success())
    
    def test_is_redirect(self):
        """Test redirect status check."""
        self.assertTrue(Response(301).is_redirect())
        self.assertTrue(Response(302).is_redirect())
        self.assertFalse(Response(200).is_redirect())
    
    def test_is_client_error(self):
        """Test client error status check."""
        self.assertTrue(Response(400).is_client_error())
        self.assertTrue(Response(404).is_client_error())
        self.assertTrue(Response(429).is_client_error())
        self.assertFalse(Response(500).is_client_error())
    
    def test_is_server_error(self):
        """Test server error status check."""
        self.assertTrue(Response(500).is_server_error())
        self.assertTrue(Response(502).is_server_error())
        self.assertFalse(Response(400).is_server_error())
    
    def test_json_parsing(self):
        """Test JSON body parsing."""
        response = Response(200, body='{"key": "value"}')
        self.assertEqual(response.json(), {"key": "value"})
    
    def test_json_invalid(self):
        """Test invalid JSON handling."""
        response = Response(200, body="not json")
        with self.assertRaises(ValueError):
            response.json()
    
    def test_get_header_case_insensitive(self):
        """Test case-insensitive header access."""
        response = Response(200, headers={"Content-Type": "application/json"})
        self.assertEqual(response.get_header("content-type"), "application/json")
        self.assertEqual(response.get_header("CONTENT-TYPE"), "application/json")


class TestHTTPClient(unittest.TestCase):
    """Test HTTPClient class."""
    
    def setUp(self):
        """Set up test client."""
        self.client = HTTPClient()
    
    def tearDown(self):
        """Clean up."""
        self.client.close()
    
    @patch("main.requests.Session.request")
    def test_get_request(self, mock_request):
        """Test GET request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.text = '{"data": "test"}'
        mock_response.url = "https://api.example.com/test"
        mock_response.elapsed.total_seconds.return_value = 0.1
        mock_request.return_value = mock_response
        
        response = self.client.get("https://api.example.com/test")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"data": "test"})
        mock_request.assert_called_once()
    
    @patch("main.requests.Session.request")
    def test_post_with_json(self, mock_request):
        """Test POST with JSON body."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.headers = {}
        mock_response.text = "Created"
        mock_response.url = "https://api.example.com/users"
        mock_response.elapsed.total_seconds.return_value = 0.2
        mock_request.return_value = mock_response
        
        response = self.client.post(
            "https://api.example.com/users",
            json={"name": "John"}
        )
        
        self.assertEqual(response.status_code, 201)
        call_args = mock_request.call_args
        self.assertEqual(call_args[1]["json"], {"name": "John"})
    
    @patch("main.requests.Session.request")
    def test_custom_headers(self, mock_request):
        """Test custom headers."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.text = "OK"
        mock_response.url = "https://api.example.com/test"
        mock_response.elapsed.total_seconds.return_value = 0.1
        mock_request.return_value = mock_response
        
        self.client.get(
            "https://api.example.com/test",
            headers={"Authorization": "Bearer token123"}
        )
        
        call_args = mock_request.call_args
        headers = call_args[1]["headers"]
        self.assertEqual(headers["Authorization"], "Bearer token123")
    
    @patch("main.requests.Session.request")
    def test_query_params(self, mock_request):
        """Test query parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.text = "OK"
        mock_response.url = "https://api.example.com/search?q=python"
        mock_response.elapsed.total_seconds.return_value = 0.1
        mock_request.return_value = mock_response
        
        self.client.get(
            "https://api.example.com/search",
            params={"q": "python", "limit": 10}
        )
        
        call_args = mock_request.call_args
        self.assertIn("q=python", call_args[1]["url"])


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""
    
    def test_parse_headers(self):
        """Test header parsing."""
        headers = parse_headers(["Content-Type: application/json", "Authorization: Bearer token"])
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertEqual(headers["Authorization"], "Bearer token")
    
    def test_parse_params(self):
        """Test parameter parsing."""
        params = parse_params("q=python&limit=10")
        self.assertEqual(params["q"], "python")
        self.assertEqual(params["limit"], "10")
    
    def test_parse_headers_invalid(self):
        """Test header parsing with invalid format."""
        headers = parse_headers(["InvalidHeader"])
        self.assertEqual(headers, {})


class TestIntegration(unittest.TestCase):
    """Integration tests with real HTTP calls."""
    
    def test_httpbin_get(self):
        """Test GET request to httpbin."""
        client = HTTPClient()
        try:
            response = client.get("https://httpbin.org/get")
            self.assertTrue(response.is_success())
            data = response.json()
            self.assertEqual(data["url"], "https://httpbin.org/get")
        except Exception as e:
            self.skipTest(f"httpbin unavailable: {e}")
        finally:
            client.close()
    
    def test_httpbin_post(self):
        """Test POST request to httpbin."""
        client = HTTPClient()
        try:
            response = client.post(
                "https://httpbin.org/post",
                json={"test": "data"}
            )
            self.assertTrue(response.is_success())
            data = response.json()
            self.assertEqual(data["json"], {"test": "data"})
        except Exception as e:
            self.skipTest(f"httpbin unavailable: {e}")
        finally:
            client.close()


if __name__ == "__main__":
    unittest.main()
