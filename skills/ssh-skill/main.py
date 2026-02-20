#!/usr/bin/env python3
"""
SSH Remote Management Skill
===========================
SSH remote management with command execution, file transfer, and key management.

Use when scanning networks, managing remote servers, or when user mentions 
'SSH', 'DNS', 'network'.

Author: Kimi Skills Team
License: MIT
"""

import os
import json
import socket
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import paramiko
from paramiko import SSHClient, SFTPClient, RSAKey, Ed25519Key, ECDSAKey
from paramiko.ssh_exception import (
    AuthenticationException,
    SSHException,
    NoValidConnectionsError
)
from scp import SCPClient
import getpass


@dataclass
class SSHResult:
    """Data class for SSH command results."""
    command: str
    stdout: str
    stderr: str
    exit_code: int
    execution_time: float
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class TransferResult:
    """Data class for file transfer results."""
    local_path: str
    remote_path: str
    direction: str  # 'upload' or 'download'
    status: str
    file_size: int = 0
    transfer_time: float = 0.0
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class KeyInfo:
    """Data class for SSH key information."""
    key_type: str
    fingerprint: str
    comment: str
    path: str
    size: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class SSHSkill:
    """
    SSH Remote Management Skill class.
    
    Provides comprehensive SSH capabilities:
    - Remote command execution
    - Secure file transfer (SCP/SFTP)
    - SSH key generation and management
    - Connection pooling
    - Multi-host operations
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize SSHSkill.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.default_port = self.config.get("default_port", 22)
        self.default_timeout = self.config.get("default_timeout", 30)
        self.max_connections = self.config.get("max_connections", 10)
        self.key_types = self.config.get("key_types", ["ed25519", "rsa", "ecdsa"])
        self._connections: Dict[str, SSHClient] = {}

    def _get_connection_key(
        self,
        hostname: str,
        username: str,
        port: int
    ) -> str:
        """Generate connection key."""
        return f"{username}@{hostname}:{port}"

    def _load_private_key(
        self,
        key_path: str,
        password: Optional[str] = None
    ) -> paramiko.PKey:
        """Load private key from file."""
        key_classes = [
            (RSAKey, "RSA"),
            (Ed25519Key, "ED25519"),
            (ECDSAKey, "ECDSA")
        ]
        
        for key_class, key_type in key_classes:
            try:
                return key_class.from_private_key_file(key_path, password)
            except SSHException:
                continue
        
        raise SSHException(f"Unable to load private key: {key_path}")

    def connect(
        self,
        hostname: str,
        username: str,
        password: Optional[str] = None,
        key_path: Optional[str] = None,
        key_password: Optional[str] = None,
        port: int = 22,
        timeout: int = 30,
        allow_agent: bool = True,
        look_for_keys: bool = True
    ) -> SSHClient:
        """
        Establish SSH connection.
        
        Args:
            hostname: Remote host
            username: SSH username
            password: Password authentication
            key_path: Path to private key
            key_password: Password for encrypted key
            port: SSH port
            timeout: Connection timeout
            allow_agent: Allow SSH agent
            look_for_keys: Look for keys in ~/.ssh
            
        Returns:
            SSHClient instance
        """
        conn_key = self._get_connection_key(hostname, username, port)
        
        # Return existing connection if available
        if conn_key in self._connections:
            client = self._connections[conn_key]
            try:
                # Test connection
                client.exec_command("echo")
                return client
            except:
                # Connection dead, remove it
                del self._connections[conn_key]
        
        client = SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        connect_kwargs = {
            "hostname": hostname,
            "port": port,
            "username": username,
            "timeout": timeout,
            "allow_agent": allow_agent,
            "look_for_keys": look_for_keys
        }
        
        if password:
            connect_kwargs["password"] = password
        elif key_path:
            pkey = self._load_private_key(key_path, key_password)
            connect_kwargs["pkey"] = pkey
        
        try:
            client.connect(**connect_kwargs)
            self._connections[conn_key] = client
            return client
        except AuthenticationException as e:
            raise AuthenticationException(f"Authentication failed: {e}")
        except NoValidConnectionsError as e:
            raise NoValidConnectionsError(f"Unable to connect: {e}")
        except Exception as e:
            raise SSHException(f"Connection error: {e}")

    def execute(
        self,
        hostname: str,
        command: str,
        username: str,
        password: Optional[str] = None,
        key_path: Optional[str] = None,
        port: int = 22,
        timeout: Optional[int] = None,
        sudo: bool = False,
        sudo_password: Optional[str] = None,
        env: Optional[Dict[str, str]] = None
    ) -> SSHResult:
        """
        Execute command on remote host.
        
        Args:
            hostname: Remote host
            command: Command to execute
            username: SSH username
            password: Password for authentication
            key_path: Path to private key
            port: SSH port
            timeout: Command timeout
            sudo: Run with sudo
            sudo_password: Sudo password
            env: Environment variables
            
        Returns:
            SSHResult object
        """
        import time
        start_time = time.time()
        
        try:
            client = self.connect(
                hostname=hostname,
                username=username,
                password=password,
                key_path=key_path,
                port=port
            )
            
            # Prepare command
            if sudo:
                if sudo_password:
                    command = f"echo '{sudo_password}' | sudo -S {command}"
                else:
                    command = f"sudo {command}"
            
            # Set environment if provided
            if env:
                env_str = " ".join([f'{k}="{v}"' for k, v in env.items()])
                command = f"{env_str} {command}"
            
            stdin, stdout, stderr = client.exec_command(
                command,
                timeout=timeout or self.default_timeout
            )
            
            exit_code = stdout.channel.recv_exit_status()
            stdout_data = stdout.read().decode('utf-8', errors='replace')
            stderr_data = stderr.read().decode('utf-8', errors='replace')
            
            execution_time = time.time() - start_time
            
            return SSHResult(
                command=command,
                stdout=stdout_data,
                stderr=stderr_data,
                exit_code=exit_code,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return SSHResult(
                command=command,
                stdout="",
                stderr="",
                exit_code=-1,
                execution_time=execution_time,
                error=str(e)
            )

    def upload(
        self,
        hostname: str,
        local_path: str,
        remote_path: str,
        username: str,
        password: Optional[str] = None,
        key_path: Optional[str] = None,
        port: int = 22
    ) -> TransferResult:
        """
        Upload file to remote host.
        
        Args:
            hostname: Remote host
            local_path: Local file path
            remote_path: Remote destination path
            username: SSH username
            password: Password for authentication
            key_path: Path to private key
            port: SSH port
            
        Returns:
            TransferResult object
        """
        import time
        start_time = time.time()
        
        local_file = Path(local_path)
        if not local_file.exists():
            return TransferResult(
                local_path=local_path,
                remote_path=remote_path,
                direction="upload",
                status="error",
                error="Local file not found"
            )
        
        try:
            client = self.connect(
                hostname=hostname,
                username=username,
                password=password,
                key_path=key_path,
                port=port
            )
            
            with SCPClient(client.get_transport()) as scp:
                scp.put(local_path, remote_path)
            
            transfer_time = time.time() - start_time
            
            return TransferResult(
                local_path=local_path,
                remote_path=remote_path,
                direction="upload",
                status="success",
                file_size=local_file.stat().st_size,
                transfer_time=transfer_time
            )
            
        except Exception as e:
            return TransferResult(
                local_path=local_path,
                remote_path=remote_path,
                direction="upload",
                status="error",
                error=str(e)
            )

    def download(
        self,
        hostname: str,
        remote_path: str,
        local_path: str,
        username: str,
        password: Optional[str] = None,
        key_path: Optional[str] = None,
        port: int = 22
    ) -> TransferResult:
        """
        Download file from remote host.
        
        Args:
            hostname: Remote host
            remote_path: Remote file path
            local_path: Local destination path
            username: SSH username
            password: Password for authentication
            key_path: Path to private key
            port: SSH port
            
        Returns:
            TransferResult object
        """
        import time
        start_time = time.time()
        
        try:
            client = self.connect(
                hostname=hostname,
                username=username,
                password=password,
                key_path=key_path,
                port=port
            )
            
            with SCPClient(client.get_transport()) as scp:
                scp.get(remote_path, local_path)
            
            transfer_time = time.time() - start_time
            local_file = Path(local_path)
            file_size = local_file.stat().st_size if local_file.exists() else 0
            
            return TransferResult(
                local_path=local_path,
                remote_path=remote_path,
                direction="download",
                status="success",
                file_size=file_size,
                transfer_time=transfer_time
            )
            
        except Exception as e:
            return TransferResult(
                local_path=local_path,
                remote_path=remote_path,
                direction="download",
                status="error",
                error=str(e)
            )

    def generate_key(
        self,
        key_type: str = "ed25519",
        comment: str = "",
        output_path: Optional[str] = None,
        password: Optional[str] = None,
        bits: int = 4096
    ) -> KeyInfo:
        """
        Generate SSH key pair.
        
        Args:
            key_type: Type of key (rsa, ed25519, ecdsa)
            comment: Key comment
            output_path: Output directory
            password: Key passphrase
            bits: Key size (RSA only)
            
        Returns:
            KeyInfo object
        """
        if output_path is None:
            ssh_dir = Path.home() / ".ssh"
            ssh_dir.mkdir(mode=0o700, exist_ok=True)
            output_path = str(ssh_dir / f"id_{key_type}")
        
        output = Path(output_path)
        private_key_path = str(output)
        public_key_path = f"{private_key_path}.pub"
        
        try:
            if key_type == "rsa":
                key = RSAKey.generate(bits=bits)
            elif key_type == "ed25519":
                key = Ed25519Key.generate()
            elif key_type == "ecdsa":
                key = ECDSAKey.generate()
            else:
                raise ValueError(f"Unsupported key type: {key_type}")
            
            # Save private key
            key.write_private_key_file(private_key_path, password=password)
            os.chmod(private_key_path, 0o600)
            
            # Save public key
            public_key = f"{key.get_name()} {key.get_base64()}"
            if comment:
                public_key += f" {comment}"
            
            with open(public_key_path, "w") as f:
                f.write(public_key)
            os.chmod(public_key_path, 0o644)
            
            # Get fingerprint
            fingerprint = key.get_fingerprint().hex()
            
            return KeyInfo(
                key_type=key_type.upper(),
                fingerprint=fingerprint,
                comment=comment,
                path=private_key_path,
                size=bits if key_type == "rsa" else 256
            )
            
        except Exception as e:
            raise SSHException(f"Key generation failed: {e}")

    def list_keys(self, ssh_dir: Optional[str] = None) -> List[KeyInfo]:
        """
        List SSH keys in directory.
        
        Args:
            ssh_dir: SSH directory path
            
        Returns:
            List of KeyInfo objects
        """
        if ssh_dir is None:
            ssh_dir = Path.home() / ".ssh"
        else:
            ssh_dir = Path(ssh_dir)
        
        keys = []
        
        for key_file in ssh_dir.glob("id_*"):
            if key_file.suffix == ".pub":
                continue
            
            pub_file = Path(f"{key_file}.pub")
            if pub_file.exists():
                try:
                    with open(pub_file) as f:
                        content = f.read().strip()
                    parts = content.split()
                    
                    key_type = parts[0] if len(parts) > 0 else "unknown"
                    comment = parts[2] if len(parts) > 2 else ""
                    
                    # Load to get fingerprint
                    try:
                        key = self._load_private_key(str(key_file))
                        fingerprint = key.get_fingerprint().hex()
                    except:
                        fingerprint = "unknown"
                    
                    keys.append(KeyInfo(
                        key_type=key_type.upper(),
                        fingerprint=fingerprint,
                        comment=comment,
                        path=str(key_file),
                        size=0
                    ))
                except:
                    pass
        
        return keys

    def close_all(self):
        """Close all active connections."""
        for conn_key, client in list(self._connections.items()):
            try:
                client.close()
            except:
                pass
        self._connections.clear()


# Entry points for Kimi Skills Framework
def ssh_command(
    hostname: str,
    command: str,
    username: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Execute SSH command.
    
    Args:
        hostname: Remote host
        command: Command to execute
        username: SSH username
        **kwargs: Additional parameters
        
    Returns:
        Execution result dictionary
    """
    skill = SSHSkill()
    result = skill.execute(hostname, command, username, **kwargs)
    return result.to_dict()


def upload_file(
    hostname: str,
    local_path: str,
    remote_path: str,
    username: str,
    **kwargs
) -> Dict[str, Any]:
    """Upload file entry point."""
    skill = SSHSkill()
    result = skill.upload(hostname, local_path, remote_path, username, **kwargs)
    return result.to_dict()


def download_file(
    hostname: str,
    remote_path: str,
    local_path: str,
    username: str,
    **kwargs
) -> Dict[str, Any]:
    """Download file entry point."""
    skill = SSHSkill()
    result = skill.download(hostname, remote_path, local_path, username, **kwargs)
    return result.to_dict()


def generate_ssh_key(**kwargs) -> Dict[str, Any]:
    """Generate SSH key entry point."""
    skill = SSHSkill()
    result = skill.generate_key(**kwargs)
    return result.to_dict()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="SSH Remote Management Skill")
    parser.add_argument("hostname", help="Remote hostname")
    parser.add_argument("-u", "--username", required=True)
    parser.add_argument("-p", "--password")
    parser.add_argument("-k", "--key")
    parser.add_argument("-c", "--command", help="Command to execute")
    parser.add_argument("--upload", nargs=2, metavar=("LOCAL", "REMOTE"))
    parser.add_argument("--download", nargs=2, metavar=("REMOTE", "LOCAL"))
    parser.add_argument("--gen-key", action="store_true")
    
    args = parser.parse_args()
    
    if args.command:
        result = ssh_command(args.hostname, args.command, args.username,
                           password=args.password, key_path=args.key)
    elif args.upload:
        result = upload_file(args.hostname, args.upload[0], args.upload[1],
                           args.username, password=args.password, key_path=args.key)
    elif args.download:
        result = download_file(args.hostname, args.download[0], args.download[1],
                             args.username, password=args.password, key_path=args.key)
    elif args.gen_key:
        result = generate_ssh_key()
    else:
        print("Please specify --command, --upload, --download, or --gen-key")
        sys.exit(1)
    
    print(json.dumps(result, indent=2))
