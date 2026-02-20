#!/usr/bin/env python3
"""
Tests for Nginx Skill
"""

import unittest
import sys
import os
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.main import (
    NginxManager, VirtualHostConfig, UpstreamConfig,
    ServerConfig, LocationConfig
)

class TestNginxManager(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.nginx = NginxManager(self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_ensure_directories(self):
        """Test directory creation"""
        self.nginx.ensure_directories()
        
        self.assertTrue(self.nginx.sites_available.exists())
        self.assertTrue(self.nginx.sites_enabled.exists())
        self.assertTrue(self.nginx.conf_d.exists())
    
    def test_create_vhost(self):
        """Test virtual host creation"""
        config = VirtualHostConfig(
            server_name="test.com",
            port=80,
            document_root="/var/www/test"
        )
        
        path = self.nginx.create_vhost(config, enable=False)
        
        self.assertTrue(Path(path).exists())
        content = Path(path).read_text()
        self.assertIn("server_name test.com", content)
        self.assertIn("listen 80", content)
        self.assertIn("root /var/www/test", content)
    
    def test_create_ssl_vhost(self):
        """Test SSL virtual host creation"""
        config = VirtualHostConfig(
            server_name="secure.test.com",
            port=443,
            document_root="/var/www/secure",
            ssl_enabled=True,
            ssl_cert_path="/etc/ssl/cert.pem",
            ssl_key_path="/etc/ssl/key.pem"
        )
        
        path = self.nginx.create_vhost(config, enable=False)
        content = Path(path).read_text()
        
        self.assertIn("listen 443 ssl", content)
        self.assertIn("ssl_certificate", content)
        self.assertIn("ssl_certificate_key", content)
    
    def test_create_upstream(self):
        """Test upstream/load balancer creation"""
        servers = [
            ServerConfig("192.168.1.1:8080", weight=5),
            ServerConfig("192.168.1.2:8080", weight=5)
        ]
        
        config = UpstreamConfig(
            upstream_name="backend",
            upstream_servers=servers,
            load_balance_method="least_conn"
        )
        
        path = self.nginx.create_upstream(config)
        
        self.assertTrue(Path(path).exists())
        content = Path(path).read_text()
        self.assertIn("upstream backend", content)
        self.assertIn("least_conn", content)
    
    def test_enable_disable_site(self):
        """Test site enable/disable functionality"""
        config = VirtualHostConfig(server_name="enable-test.com")
        self.nginx.create_vhost(config, enable=False)
        
        # Enable
        result = self.nginx.enable_site("enable-test.com")
        self.assertTrue(result)
        self.assertTrue((self.nginx.sites_enabled / "enable-test.com.conf").exists())
        
        # Disable
        result = self.nginx.disable_site("enable-test.com")
        self.assertTrue(result)
        self.assertFalse((self.nginx.sites_enabled / "enable-test.com.conf").exists())
    
    def test_list_sites(self):
        """Test listing sites"""
        # Create some test sites
        self.nginx.create_vhost(VirtualHostConfig("site1.com"), enable=True)
        self.nginx.create_vhost(VirtualHostConfig("site2.com"), enable=False)
        
        sites = self.nginx.list_sites()
        
        self.assertIn("site1.com", sites["available"])
        self.assertIn("site2.com", sites["available"])
        self.assertIn("site1.com", sites["enabled"])
        self.assertIn("site2.com", sites["disabled"])

class TestVirtualHostConfig(unittest.TestCase):
    
    def test_default_values(self):
        """Test default configuration values"""
        config = VirtualHostConfig(server_name="test.com")
        
        self.assertEqual(config.port, 80)
        self.assertEqual(config.document_root, "/var/www/html")
        self.assertFalse(config.ssl_enabled)
        self.assertTrue(config.gzip_enabled)

class TestUpstreamConfig(unittest.TestCase):
    
    def test_server_config(self):
        """Test server configuration"""
        server = ServerConfig("127.0.0.1:8080", weight=3, backup=True)
        
        self.assertEqual(server.address, "127.0.0.1:8080")
        self.assertEqual(server.weight, 3)
        self.assertTrue(server.backup)

if __name__ == "__main__":
    unittest.main()
