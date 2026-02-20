#!/usr/bin/env python3
"""
Tests for dns-skill
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import DNSSkill, DNSRecord, DNSQueryResult, ReverseDNSResult
from main import query, resolve, reverse_lookup, get_nameservers, check_propagation


class MockDNSAnswer:
    """Mock DNS answer for testing."""
    
    def __init__(self, qname, ttl=3600):
        self.qname = qname
        self.ttl = ttl


class TestDNSSkill(unittest.TestCase):
    """Test cases for DNSSkill."""

    def setUp(self):
        """Set up test fixtures."""
        self.skill = DNSSkill()

    def test_init(self):
        """Test skill initialization."""
        self.assertEqual(self.skill.default_nameserver, "8.8.8.8")
        self.assertEqual(self.skill.default_timeout, 5)

    @patch('dns.resolver.Resolver.resolve')
    def test_query_a_record(self, mock_resolve):
        """Test A record query."""
        # Mock DNS answer
        mock_answer = Mock()
        mock_answer.qname = "example.com."
        mock_answer.ttl = 3600
        mock_rdata = Mock()
        mock_rdata.address = "93.184.216.34"
        mock_answer.__iter__ = Mock(return_value=iter([mock_rdata]))
        mock_resolve.return_value = mock_answer
        
        result = self.skill.query("example.com", "A")
        
        self.assertEqual(result.domain, "example.com")
        self.assertEqual(result.record_type, "A")

    @patch('dns.resolver.Resolver.resolve')
    def test_query_mx_record(self, mock_resolve):
        """Test MX record query."""
        mock_answer = Mock()
        mock_answer.qname = "example.com."
        mock_answer.ttl = 3600
        mock_rdata = Mock()
        mock_rdata.preference = 10
        mock_rdata.exchange = "mail.example.com."
        mock_answer.__iter__ = Mock(return_value=iter([mock_rdata]))
        mock_resolve.return_value = mock_answer
        
        result = self.skill.query("example.com", "MX")
        
        self.assertEqual(result.record_type, "MX")
        self.assertEqual(len(result.records), 1)

    def test_query_invalid_domain(self):
        """Test query with invalid domain."""
        result = self.skill.query("not-a-valid-domain-12345.xyz", "A")
        # Will get NXDOMAIN or similar error
        self.assertIsNotNone(result.error)

    @patch('dns.resolver.Resolver.resolve')
    def test_resolve(self, mock_resolve):
        """Test domain resolution."""
        mock_answer = Mock()
        mock_answer.__iter__ = Mock(return_value=iter([]))
        mock_resolve.return_value = mock_answer
        
        result = self.skill.resolve("example.com")
        
        self.assertEqual(result["domain"], "example.com")
        self.assertIn("ipv4", result)
        self.assertIn("ipv6", result)

    @patch('dns.resolver.Resolver.resolve')
    def test_reverse_lookup(self, mock_resolve):
        """Test reverse DNS lookup."""
        mock_answer = Mock()
        mock_rdata = Mock()
        mock_rdata.__str__ = Mock(return_value="dns.google.")
        mock_answer.__iter__ = Mock(return_value=iter([mock_rdata]))
        mock_resolve.return_value = mock_answer
        
        result = self.skill.reverse_lookup("8.8.8.8")
        
        self.assertEqual(result.ip, "8.8.8.8")

    def test_reverse_lookup_invalid_ip(self):
        """Test reverse lookup with invalid IP."""
        result = self.skill.reverse_lookup("not-an-ip")
        
        self.assertEqual(result.ip, "not-an-ip")
        self.assertIn("Invalid IP", result.error)

    @patch('dns.resolver.Resolver.resolve')
    def test_get_nameservers(self, mock_resolve):
        """Test getting nameservers."""
        mock_answer = Mock()
        mock_answer.qname = "example.com."
        mock_answer.ttl = 3600
        mock_rdata = Mock()
        mock_rdata.__str__ = Mock(return_value="ns1.example.com.")
        mock_answer.__iter__ = Mock(return_value=iter([mock_rdata]))
        mock_resolve.return_value = mock_answer
        
        result = self.skill.get_nameservers("example.com")
        
        self.assertEqual(result["domain"], "example.com")
        self.assertIsInstance(result["nameservers"], list)

    def test_dns_record_to_dict(self):
        """Test DNSRecord conversion to dict."""
        record = DNSRecord(
            name="example.com",
            type="A",
            ttl=3600,
            data="93.184.216.34"
        )
        
        data = record.to_dict()
        self.assertEqual(data["name"], "example.com")
        self.assertEqual(data["type"], "A")

    def test_dns_query_result_to_dict(self):
        """Test DNSQueryResult conversion to dict."""
        record = DNSRecord(
            name="example.com",
            type="A",
            ttl=3600,
            data="93.184.216.34"
        )
        result = DNSQueryResult(
            domain="example.com",
            record_type="A",
            nameserver="8.8.8.8",
            records=[record],
            query_time=0.05
        )
        
        data = result.to_dict()
        self.assertEqual(data["domain"], "example.com")
        self.assertEqual(len(data["records"]), 1)

    def test_reverse_dns_result_to_dict(self):
        """Test ReverseDNSResult conversion to dict."""
        result = ReverseDNSResult(
            ip="8.8.8.8",
            hostnames=["dns.google"],
            query_time=0.05
        )
        
        data = result.to_dict()
        self.assertEqual(data["ip"], "8.8.8.8")
        self.assertEqual(data["hostnames"], ["dns.google"])

    @patch.object(DNSSkill, 'query')
    def test_check_propagation(self, mock_query):
        """Test DNS propagation check."""
        mock_result = DNSQueryResult(
            domain="example.com",
            record_type="A",
            nameserver="8.8.8.8",
            records=[DNSRecord(
                name="example.com",
                type="A",
                ttl=3600,
                data="93.184.216.34"
            )],
            query_time=0.05
        )
        mock_query.return_value = mock_result
        
        result = self.skill.check_propagation(
            "example.com",
            "A",
            nameservers=["8.8.8.8"]
        )
        
        self.assertEqual(result["domain"], "example.com")
        self.assertIn("propagated", result)


class TestIntegration(unittest.TestCase):
    """Integration tests - make real DNS queries."""

    @unittest.skip("Makes real DNS queries")
    def test_real_a_record_query(self):
        """Test real A record query."""
        result = query("google.com", "A")
        
        self.assertIsNone(result.get("error"))
        self.assertTrue(len(result["records"]) > 0)

    @unittest.skip("Makes real DNS queries")
    def test_real_mx_query(self):
        """Test real MX record query."""
        result = query("google.com", "MX")
        
        self.assertIsNone(result.get("error"))
        # Google should have MX records
        self.assertTrue(len(result["records"]) > 0)

    @unittest.skip("Makes real DNS queries")
    def test_real_reverse_lookup(self):
        """Test real reverse DNS lookup."""
        result = reverse_lookup("8.8.8.8")
        
        self.assertIsNone(result.get("error"))
        self.assertTrue(len(result["hostnames"]) > 0)


if __name__ == "__main__":
    unittest.main()
