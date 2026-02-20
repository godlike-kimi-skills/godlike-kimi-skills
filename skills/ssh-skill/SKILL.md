# ssh-skill

SSH remote management tool with command execution, file transfer, and key management.

Use when scanning networks, managing remote servers, or when user mentions 'SSH', 'DNS', 'network'.

## Overview

This skill provides comprehensive SSH functionality for remote server management, including command execution, file transfers, and SSH key operations.

## Triggers

- "ssh"
- "remote command"
- "scp"
- "upload file"
- "download file"
- "remote server"
- "key generation"

## Functions

### ssh_command(hostname, command, username, **kwargs)

Execute a command on a remote server.

**Parameters:**
- `hostname` (str): Remote server hostname or IP
- `command` (str): Command to execute
- `username` (str): SSH username
- `password` (str): Password for authentication
- `key_path` (str): Path to private key file
- `port` (int): SSH port (default: 22)
- `timeout` (int): Command timeout
- `sudo` (bool): Execute with sudo
- `sudo_password` (str): Sudo password
- `env` (dict): Environment variables

**Returns:**
Dictionary with stdout, stderr, exit code, and execution time.

### upload_file(hostname, local_path, remote_path, username, **kwargs)

Upload a file to remote server.

**Parameters:**
- `hostname` (str): Remote server
- `local_path` (str): Local file path
- `remote_path` (str): Remote destination path
- `username`, `password`, `key_path`: Authentication options

**Returns:**
Transfer result with status and metrics.

### download_file(hostname, remote_path, local_path, username, **kwargs)

Download a file from remote server.

**Parameters:**
- `hostname` (str): Remote server
- `remote_path` (str): Remote file path
- `local_path` (str): Local destination path

**Returns:**
Transfer result with status and metrics.

### generate_ssh_key(**kwargs)

Generate a new SSH key pair.

**Parameters:**
- `key_type` (str): "rsa", "ed25519", or "ecdsa"
- `comment` (str): Key comment
- `output_path` (str): Output path for key files
- `password` (str): Passphrase for private key
- `bits` (int): Key size (RSA only)

**Returns:**
Key information including fingerprint and path.

## Examples

```python
# Execute simple command
ssh_command("server.com", "uptime", "admin", password="pass")

# Execute with key auth
ssh_command("server.com", "whoami", "admin", key_path="~/.ssh/id_rsa")

# Sudo command
ssh_command("server.com", "apt update", "admin", 
           password="pass", sudo=True, sudo_password="sudo_pass")

# Upload file
upload_file("server.com", "local.txt", "/remote/path", "admin", key_path="~/.ssh/id_rsa")

# Download file
download_file("server.com", "/remote/file.txt", "local.txt", "admin", password="pass")

# Generate ED25519 key
generate_ssh_key(key_type="ed25519", comment="my-server")
```

## Authentication Methods

1. **Password**: Simple but less secure
2. **Key File**: Recommended for automation
3. **SSH Agent**: Automatic key discovery
4. **Key with Passphrase**: Most secure option

## Connection Management

The skill automatically manages connections:
- Reuses existing connections
- Handles connection timeouts
- Properly closes connections on exit

## Requirements

- Python 3.8+
- paramiko, scp
- SSH server on remote host
