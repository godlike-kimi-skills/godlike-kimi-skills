#!/usr/bin/env python3
"""
Tests for nmap-skill
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import NmapSkill, ScanType, ScanIntensity, ScanResult, scan


class TestNmapSkill(unittest.TestCase):
    """Test cases for NmapSkill."""

    def setUp(self):
        """Set up test fixtures."""
        self.skill = NmapSkill()

    def test_validate_target_valid_ip(self):
        """Test valid IP validation."""
        self.assertTrue(self.skill._validate_target("192.168.1.1"))
        self.assertTrue(self.skill._validate_target("10.0.0.1"))

    def test_validate_target_valid_hostname(self):
        """Test valid hostname validation."""
        self.assertTrue(self.skill._validate_target("example.com"))
        self.assertTrue(self.skill._validate_target("sub.domain.example.com"))

    def test_validate_target_valid_cidr(self):
        """Test valid CIDR validation."""
        self.assertTrue(self.skill._validate_target("192.168.1.0/24"))
        self.assertTrue(self.skill._validate_target("10.0.0.0/8"))

    def test_validate_target_invalid(self):
        """Test invalid target validation."""
        self.assertFalse(self.skill._validate_target(""))
        self.assertFalse(self.skill._validate_target("not a valid target"))
        self.assertFalse(self.skill._validate_target("256.256.256.256"))

    def test_build_command_basic(self):
        """Test basic command building."""
        cmd = self.skill._build_command(
            target="192.168.1.1",
            ports="80,443"
        )
        
        self.assertIn("nmap", cmd)
        self.assertIn("-p", cmd)
        self.assertIn("80,443", cmd)
        self.assertIn("192.168.1.1", cmd)

    def test_build_command_with_service_detection(self):
        """Test command building with service detection."""
        cmd = self.skill._build_command(
            target="example.com",
            ports="1-1000",
            service_detection=True
        )
        
        self.assertIn("-sV", cmd)

    def test_build_command_with_os_detection(self):
        """Test command building with OS detection."""
        cmd = self.skill._build_command(
            target="192.168.1.1",
            os_detection=True
        )
        
        self.assertIn("-O", cmd)

    def test_scan_types(self):
        """Test scan type enumeration."""
        self.assertEqual(ScanType.TCP_SYN.value, "-sS")
        self.assertEqual(ScanType.TCP_CONNECT.value, "-sT")
        self.assertEqual(ScanType.UDP.value, "-sU")

    def test_scan_intensities(self):
        """Test scan intensity enumeration."""
        self.assertIn("-T4", ScanIntensity.QUICK.value)
        self.assertIn("-T3", ScanIntensity.NORMAL.value)
        self.assertIn("-T2", ScanIntensity.INTENSIVE.value)

    @patch('main.subprocess.run')
    @patch('main.NmapSkill._find_nmap')
    def test_scan_success(self, mock_find_nmap, mock_run):
        """Test successful scan execution."""
        mock_find_nmap.return_value = "/usr/bin/nmap"
        
        # Create mock XML output
        mock_xml = """<?xml version="1.0"?>
        <nmaprun>
            <host>
                <status state="up"/>
                <address addr="192.168.1.1"/>
                <ports>
                    <port portid="80" protocol="tcp">
                        <state state="open"/>
                        <service name="http"/>
                    </port>
                </ports>
            </host>
        </nmaprun>"""
        
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        
        with patch('tempfile.NamedTemporaryFile') as mock_temp:
            mock_file = Mock()
            mock_file.name = "/tmp/test.xml"
            mock_temp.return_value.__enter__ = Mock(return_value=mock_file)
            mock_temp.return_value.__exit__ = Mock(return_value=False)
            
            with patch('main.NmapSkill._parse_xml_output') as mock_parse:
                mock_parse.return_value = [
                    ScanResult(
                        host="192.168.1.1",
                        state="up",
                        ports=[{"port": "80", "state": "open"}]
                    )
                ]
                
                result = scan("192.168.1.1")
                
                self.assertTrue(result["success"])
                self.assertEqual(result["target"], "192.168.1.1")

    def test_scan_invalid_target(self):
        """Test scan with invalid target."""
        result = scan("not-a-valid-target")
        
        self.assertFalse(result["success"])
        self.assertIn("Invalid target", result["error"])

    def test_scan_result_to_dict(self):
        """Test ScanResult conversion to dict."""
        result = ScanResult(
            host="192.168.1.1",
            state="up",
            ports=[{"port": "80", "state": "open"}],
            scan_time=5.0
        )
        
        data = result.to_dict()
        self.assertEqual(data["host"], "192.168.1.1")
        self.assertEqual(data["state"], "up")


class TestIntegration(unittest.TestCase):
    """Integration tests."""

    @unittest.skip("Requires nmap to be installed")
    def test_real_scan_localhost(self):
        """Test real scan against localhost (requires nmap)."""
        result = scan("127.0.0.1", ports="22,80,443")
        
        self.assertIn("success", result)
        self.assertIn("results", result)


if __name__ == "__main__":
    unittest.main()
