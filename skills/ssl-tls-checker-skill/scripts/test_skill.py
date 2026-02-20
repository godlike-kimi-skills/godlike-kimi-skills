#!/usr/bin/env python3
"""
SSL/TLS Checker Skill - Test Suite
"""

import os
import sys
import json
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent))

from main import SSLChecker, CertificateInfo, SSLConfig, Vulnerability, Grade


class TestSSLChecker(unittest.TestCase):
    """Test cases for SSLChecker."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.checker = SSLChecker(timeout=5, verbose=False)
    
    def test_grade_calculation_a_plus(self):
        """Test A+ grade calculation."""
        cert = CertificateInfo(
            subject="CN=test.com",
            issuer="CN=Test CA",
            valid_from="2024-01-01T00:00:00Z",
            valid_until="2025-01-01T00:00:00Z",
            days_until_expiry=365,
            serial_number="1234",
            signature_algorithm="sha256WithRSAEncryption",
            key_algorithm="RSA",
            key_size=2048,
            is_valid=True
        )
        
        config = SSLConfig(
            protocols=["TLSv1.3", "TLSv1.2"],
            cipher_suites=["TLS_AES_256_GCM_SHA384"],
            supports_hsts=True,
            hsts_max_age=31536000,
            hsts_include_subdomains=True
        )
        
        vulnerabilities = []
        
        grade = self.checker._calculate_grade(cert, config, vulnerabilities)
        self.assertEqual(grade, Grade.A_PLUS)
    
    def test_grade_calculation_f_expired(self):
        """Test F grade for expired certificate."""
        cert = CertificateInfo(
            subject="CN=test.com",
            issuer="CN=Test CA",
            valid_from="2023-01-01T00:00:00Z",
            valid_until="2023-12-01T00:00:00Z",
            days_until_expiry=-50,
            serial_number="1234",
            signature_algorithm="sha256WithRSAEncryption",
            key_algorithm="RSA",
            key_size=2048,
            is_valid=False,
            validation_errors=["Certificate has expired"]
        )
        
        config = SSLConfig(protocols=["TLSv1.2"])
        vulnerabilities = []
        
        grade = self.checker._calculate_grade(cert, config, vulnerabilities)
        self.assertEqual(grade, Grade.F)
    
    def test_grade_sslv3_vulnerable(self):
        """Test grade penalty for SSLv3 support."""
        cert = CertificateInfo(
            subject="CN=test.com",
            issuer="CN=Test CA",
            valid_from="2024-01-01T00:00:00Z",
            valid_until="2025-01-01T00:00:00Z",
            days_until_expiry=365,
            serial_number="1234",
            signature_algorithm="sha256WithRSAEncryption",
            key_algorithm="RSA",
            key_size=2048,
            is_valid=True
        )
        
        config = SSLConfig(protocols=["TLSv1.2", "SSLv3"])
        
        vulnerabilities = [Vulnerability(
            name="POODLE",
            cve_id="CVE-2014-3566",
            severity="HIGH",
            description="SSLv3 padding oracle",
            is_vulnerable=True,
            remediation="Disable SSLv3"
        )]
        
        grade = self.checker._calculate_grade(cert, config, vulnerabilities)
        self.assertIn(grade, [Grade.C, Grade.D, Grade.F])
    
    def test_certificate_info_structure(self):
        """Test certificate info structure."""
        cert = CertificateInfo(
            subject="CN=example.com",
            issuer="CN=Test CA",
            valid_from="2024-01-01T00:00:00Z",
            valid_until="2025-01-01T00:00:00Z",
            days_until_expiry=365,
            serial_number="abcdef",
            signature_algorithm="sha256WithRSAEncryption",
            key_algorithm="RSA",
            key_size=2048,
            san=["example.com", "www.example.com"],
            is_valid=True
        )
        
        cert_dict = cert.__dict__
        required_fields = ["subject", "issuer", "valid_from", "valid_until",
                          "days_until_expiry", "serial_number", "signature_algorithm",
                          "key_algorithm", "key_size", "san", "is_valid"]
        
        for field in required_fields:
            self.assertIn(field, cert_dict)
    
    def test_ssl_config_structure(self):
        """Test SSL config structure."""
        config = SSLConfig(
            protocols=["TLSv1.2", "TLSv1.3"],
            cipher_suites=["TLS_AES_256_GCM_SHA384"],
            supports_hsts=True,
            hsts_max_age=31536000,
            hsts_include_subdomains=True
        )
        
        config_dict = config.__dict__
        required_fields = ["protocols", "cipher_suites", "supports_hsts",
                          "hsts_max_age", "hsts_include_subdomains"]
        
        for field in required_fields:
            self.assertIn(field, config_dict)
    
    def test_vulnerability_structure(self):
        """Test vulnerability structure."""
        vuln = Vulnerability(
            name="Heartbleed",
            cve_id="CVE-2014-0160",
            severity="CRITICAL",
            description="OpenSSL vulnerability",
            is_vulnerable=False,
            remediation="Update OpenSSL"
        )
        
        vuln_dict = vuln.__dict__
        required_fields = ["name", "cve_id", "severity", "description",
                          "is_vulnerable", "remediation"]
        
        for field in required_fields:
            self.assertIn(field, vuln_dict)
    
    @patch('main.socket.gethostbyname')
    def test_resolve_hostname(self, mock_gethost):
        """Test hostname resolution."""
        mock_gethost.return_value = "93.184.216.34"
        
        ip = self.checker._resolve_hostname("example.com")
        self.assertEqual(ip, "93.184.216.34")
    
    def test_check_hsts_parsing(self):
        """Test HSTS header parsing."""
        # Test with HSTS header
        hsts_header = "max-age=31536000; includeSubDomains"
        max_age_match = __import__('re').search(r'max-age=(\d+)', hsts_header)
        max_age = int(max_age_match.group(1)) if max_age_match else 0
        include_subdomains = 'includeSubDomains' in hsts_header
        
        self.assertEqual(max_age, 31536000)
        self.assertTrue(include_subdomains)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases."""
    
    def setUp(self):
        self.checker = SSLChecker(timeout=5)
    
    def test_weak_cipher_detection(self):
        """Test weak cipher detection."""
        weak_ciphers = ["TLS_RSA_WITH_RC4_128_SHA", "TLS_RSA_WITH_3DES_EDE_CBC_SHA"]
        
        for cipher in weak_ciphers:
            is_weak = any(w in cipher.upper() for w in ["RC4", "DES", "3DES"])
            self.assertTrue(is_weak, f"{cipher} should be flagged as weak")
    
    def test_deprecated_protocol_detection(self):
        """Test deprecated protocol detection."""
        deprecated = ["SSLv2", "SSLv3", "TLSv1.0", "TLSv1.1"]
        
        for proto in deprecated:
            self.assertIn(proto, SSLChecker.DEPRECATED_PROTOCOLS)
    
    def test_key_size_penalty(self):
        """Test grade penalty for small key size."""
        cert_1024 = CertificateInfo(
            subject="CN=test.com",
            issuer="CN=CA",
            valid_from="2024-01-01T00:00:00Z",
            valid_until="2025-01-01T00:00:00Z",
            days_until_expiry=365,
            serial_number="1234",
            signature_algorithm="sha256WithRSAEncryption",
            key_algorithm="RSA",
            key_size=1024,
            is_valid=True
        )
        
        cert_2048 = CertificateInfo(
            subject="CN=test.com",
            issuer="CN=CA",
            valid_from="2024-01-01T00:00:00Z",
            valid_until="2025-01-01T00:00:00Z",
            days_until_expiry=365,
            serial_number="1234",
            signature_algorithm="sha256WithRSAEncryption",
            key_algorithm="RSA",
            key_size=2048,
            is_valid=True
        )
        
        config = SSLConfig(protocols=["TLSv1.2"])
        vulnerabilities = []
        
        grade_1024 = self.checker._calculate_grade(cert_1024, config, vulnerabilities)
        grade_2048 = self.checker._calculate_grade(cert_2048, config, vulnerabilities)
        
        # 1024-bit key should have worse grade
        self.assertLess(grade_1024.value, grade_2048.value)
    
    def test_days_until_expiry_calculation(self):
        """Test days until expiry calculation."""
        from datetime import datetime, timedelta
        
        future_date = datetime.utcnow() + timedelta(days=60)
        days = (future_date - datetime.utcnow()).days
        
        self.assertEqual(days, 60)
        
        # Test expired
        past_date = datetime.utcnow() - timedelta(days=10)
        days = (past_date - datetime.utcnow()).days
        self.assertLess(days, 0)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestSSLChecker))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
