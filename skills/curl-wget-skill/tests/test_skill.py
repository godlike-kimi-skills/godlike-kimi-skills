#!/usr/bin/env python3
"""
Tests for curl-wget-skill
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import CurlWgetSkill, DownloadResult, download, batch_download


class TestCurlWgetSkill(unittest.TestCase):
    """Test cases for CurlWgetSkill."""

    def setUp(self):
        """Set up test fixtures."""
        self.skill = CurlWgetSkill()

    def test_validate_url_valid(self):
        """Test valid URL validation."""
        self.assertTrue(self.skill._validate_url("https://example.com/file.zip"))
        self.assertTrue(self.skill._validate_url("http://localhost:8080/data"))

    def test_validate_url_invalid(self):
        """Test invalid URL validation."""
        self.assertFalse(self.skill._validate_url("not-a-url"))
        self.assertFalse(self.skill._validate_url(""))
        self.assertFalse(self.skill._validate_url("ftp://example.com"))

    def test_get_filename_from_url(self):
        """Test filename extraction from URL."""
        self.assertEqual(
            self.skill._get_filename_from_url("https://example.com/file.zip"),
            "file.zip"
        )
        self.assertEqual(
            self.skill._get_filename_from_url("https://example.com/path/to/file.txt"),
            "file.txt"
        )

    def test_get_filename_from_url_no_path(self):
        """Test filename extraction with no path."""
        filename = self.skill._get_filename_from_url("https://example.com/")
        self.assertEqual(filename, "download")

    @patch('main.requests.Session.get')
    def test_download_success(self, mock_get):
        """Test successful download."""
        # Mock response
        mock_response = Mock()
        mock_response.headers = {"Content-Length": "100"}
        mock_response.status_code = 200
        mock_response.iter_content.return_value = [b"test data"]
        mock_get.return_value = mock_response
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.txt")
            result = self.skill.download(
                "https://example.com/test.txt",
                output_path=output_path
            )
            
            self.assertEqual(result.status, "success")
            self.assertEqual(result.local_path, output_path)

    def test_download_invalid_url(self):
        """Test download with invalid URL."""
        result = self.skill.download("not-a-valid-url")
        
        self.assertEqual(result.status, "error")
        self.assertIn("Invalid URL", result.error)

    @patch('main.requests.Session.head')
    def test_get_file_size(self, mock_head):
        """Test getting file size from headers."""
        mock_response = Mock()
        mock_response.headers = {"Content-Length": "1024"}
        mock_head.return_value = mock_response
        
        size = self.skill._get_file_size("https://example.com/file.zip")
        self.assertEqual(size, 1024)

    @patch('main.requests.Session.head')
    def test_supports_resume(self, mock_head):
        """Test resume capability check."""
        mock_response = Mock()
        mock_response.headers = {"Accept-Ranges": "bytes"}
        mock_head.return_value = mock_response
        
        self.assertTrue(self.skill._supports_resume("https://example.com/file.zip"))

    @patch('main.CurlWgetSkill.download')
    def test_batch_download(self, mock_download):
        """Test batch download."""
        mock_download.return_value = DownloadResult(
            url="https://example.com/file1.zip",
            status="success",
            local_path="downloads/file1.zip"
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            urls = [
                "https://example.com/file1.zip",
                "https://example.com/file2.zip"
            ]
            result = self.skill.batch_download(urls, output_dir=tmpdir)
            
            self.assertTrue(result["success"])
            self.assertEqual(result["total"], 2)

    def test_download_result_to_dict(self):
        """Test DownloadResult conversion to dict."""
        result = DownloadResult(
            url="https://example.com/file.zip",
            status="success",
            local_path="/tmp/file.zip",
            file_size=1024,
            speed=512.0
        )
        
        data = result.to_dict()
        self.assertEqual(data["url"], "https://example.com/file.zip")
        self.assertEqual(data["status"], "success")

    @patch('main.requests.Session.get')
    def test_download_with_checksum(self, mock_get):
        """Test download with checksum verification."""
        mock_response = Mock()
        mock_response.headers = {"Content-Length": "4"}
        mock_response.status_code = 200
        mock_response.iter_content.return_value = [b"test"]
        mock_get.return_value = mock_response
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.txt")
            # SHA256 of "test"
            checksum = "f2ca1bb6c7e907d06dafe4687e579fce76b37e4e93b7605022da52e6ccc26fd2"
            
            result = self.skill.download(
                "https://example.com/test.txt",
                output_path=output_path,
                verify_checksum=checksum
            )
            
            # Note: Will fail checksum because content is different
            self.assertEqual(result.status, "checksum_mismatch")


class TestIntegration(unittest.TestCase):
    """Integration tests."""

    @unittest.skip("Makes real HTTP requests")
    def test_download_real_file(self):
        """Test downloading a real file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.html")
            result = download("https://httpbin.org/html", output_path=output_path)
            
            self.assertEqual(result["status"], "success")
            self.assertTrue(os.path.exists(output_path))


if __name__ == "__main__":
    unittest.main()
