#!/usr/bin/env python3
"""
Tests for ssh-skill
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import SSHSkill, SSHResult, TransferResult, KeyInfo
from main import ssh_command, upload_file, download_file, generate_ssh_key


class MockSSHClient:
    """Mock SSH client for testing."""
    
    def __init__(self):
        self.connected = False
        self.hostname = None
        self.username = None
    
    def set_missing_host_key_policy(self, policy):
        pass
    
    def connect(self, **kwargs):
        self.connected = True
        self.hostname = kwargs.get('hostname')
        self.username = kwargs.get('username')
    
    def exec_command(self, command, timeout=None):
        stdin = Mock()
        stdout = Mock()
        stderr = Mock()
        
        stdout.read.return_value = b"command output"
        stderr.read.return_value = b""
        stdout.channel.recv_exit_status.return_value = 0
        
        return stdin, stdout, stderr
    
    def get_transport(self):
        transport = Mock()
        return transport
    
    def close(self):
        self.connected = False


class TestSSHSkill(unittest.TestCase):
    """Test cases for SSHSkill."""

    def setUp(self):
        """Set up test fixtures."""
        self.skill = SSHSkill()

    def test_get_connection_key(self):
        """Test connection key generation."""
        key = self.skill._get_connection_key("server.com", "admin", 22)
        self.assertEqual(key, "admin@server.com:22")

    @patch('main.paramiko.SSHClient')
    def test_connect(self, mock_client_class):
        """Test SSH connection."""
        mock_client = MockSSHClient()
        mock_client_class.return_value = mock_client
        
        client = self.skill.connect(
            hostname="server.com",
            username="admin",
            password="secret"
        )
        
        self.assertTrue(mock_client.connected)
        self.assertEqual(mock_client.hostname, "server.com")

    @patch('main.paramiko.SSHClient')
    def test_execute_command(self, mock_client_class):
        """Test command execution."""
        mock_client = MockSSHClient()
        mock_client_class.return_value = mock_client
        
        result = self.skill.execute(
            hostname="server.com",
            command="ls -la",
            username="admin",
            password="secret"
        )
        
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout, "command output")

    @patch('main.paramiko.SSHClient')
    @patch('main.SCPClient')
    def test_upload_file(self, mock_scp_class, mock_client_class):
        """Test file upload."""
        mock_client = MockSSHClient()
        mock_client_class.return_value = mock_client
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"test content")
            tmp.flush()
            local_path = tmp.name
        
        try:
            result = self.skill.upload(
                hostname="server.com",
                local_path=local_path,
                remote_path="/remote/file.txt",
                username="admin",
                password="secret"
            )
            
            self.assertEqual(result.status, "success")
            self.assertEqual(result.direction, "upload")
        finally:
            os.unlink(local_path)

    @patch('main.paramiko.SSHClient')
    @patch('main.SCPClient')
    def test_download_file(self, mock_scp_class, mock_client_class):
        """Test file download."""
        mock_client = MockSSHClient()
        mock_client_class.return_value = mock_client
        
        with tempfile.TemporaryDirectory() as tmpdir:
            local_path = os.path.join(tmpdir, "downloaded.txt")
            
            result = self.skill.download(
                hostname="server.com",
                remote_path="/remote/file.txt",
                local_path=local_path,
                username="admin",
                password="secret"
            )
            
            self.assertEqual(result.status, "success")
            self.assertEqual(result.direction, "download")

    def test_ssh_result_to_dict(self):
        """Test SSHResult conversion to dict."""
        result = SSHResult(
            command="ls -la",
            stdout="output",
            stderr="error",
            exit_code=0,
            execution_time=1.5
        )
        
        data = result.to_dict()
        self.assertEqual(data["command"], "ls -la")
        self.assertEqual(data["exit_code"], 0)

    def test_transfer_result_to_dict(self):
        """Test TransferResult conversion to dict."""
        result = TransferResult(
            local_path="local.txt",
            remote_path="remote.txt",
            direction="upload",
            status="success",
            file_size=1024
        )
        
        data = result.to_dict()
        self.assertEqual(data["direction"], "upload")
        self.assertEqual(data["file_size"], 1024)

    def test_key_info_to_dict(self):
        """Test KeyInfo conversion to dict."""
        key = KeyInfo(
            key_type="RSA",
            fingerprint="abc123",
            comment="test-key",
            path="~/.ssh/id_rsa",
            size=4096
        )
        
        data = key.to_dict()
        self.assertEqual(data["key_type"], "RSA")
        self.assertEqual(data["size"], 4096)

    @patch('main.paramiko.SSHClient')
    def test_sudo_command(self, mock_client_class):
        """Test sudo command execution."""
        mock_client = MockSSHClient()
        mock_client_class.return_value = mock_client
        
        result = self.skill.execute(
            hostname="server.com",
            command="apt-get update",
            username="admin",
            password="secret",
            sudo=True,
            sudo_password="sudo_pass"
        )
        
        self.assertEqual(result.exit_code, 0)

    def test_list_keys(self):
        """Test listing SSH keys."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a mock key file
            key_file = os.path.join(tmpdir, "id_rsa")
            pub_file = key_file + ".pub"
            
            with open(pub_file, "w") as f:
                f.write("ssh-rsa AAAAB3NzaC1 test@example.com")
            
            keys = self.skill.list_keys(tmpdir)
            
            self.assertEqual(len(keys), 1)
            self.assertEqual(keys[0].key_type, "SSH-RSA")


class TestIntegration(unittest.TestCase):
    """Integration tests - require real SSH server."""

    @unittest.skip("Requires real SSH server")
    def test_real_ssh_connection(self):
        """Test real SSH connection."""
        result = ssh_command(
            hostname="localhost",
            command="whoami",
            username="testuser",
            password="testpass"
        )
        
        self.assertEqual(result["exit_code"], 0)


if __name__ == "__main__":
    unittest.main()
