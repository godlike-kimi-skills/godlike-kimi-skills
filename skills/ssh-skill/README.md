# ssh-skill

SSH remote management tool with command execution, file transfer, and key management.

Use when scanning networks, managing remote servers, or when user mentions 'SSH', 'DNS', 'network'.

## Features

- **Remote Command Execution**: Execute commands on remote servers
- **Secure File Transfer**: SCP/SFTP upload and download
- **SSH Key Management**: Generate and manage SSH keys
- **Connection Pooling**: Reuse connections for efficiency
- **Sudo Support**: Execute commands with elevated privileges
- **Multi-host Operations**: Execute commands across multiple hosts

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### As a Skill

```python
from main import ssh_command, upload_file, download_file, generate_ssh_key

# Execute remote command
result = ssh_command(
    hostname="server.example.com",
    command="ls -la",
    username="admin",
    password="secret"
)

# Execute with key authentication
result = ssh_command(
    hostname="server.example.com",
    command="whoami",
    username="admin",
    key_path="~/.ssh/id_rsa"
)

# Upload file
result = upload_file(
    hostname="server.example.com",
    local_path="local_file.txt",
    remote_path="/remote/path/file.txt",
    username="admin",
    key_path="~/.ssh/id_rsa"
)

# Download file
result = download_file(
    hostname="server.example.com",
    remote_path="/remote/file.txt",
    local_path="local_file.txt",
    username="admin",
    password="secret"
)

# Generate SSH key
result = generate_ssh_key(
    key_type="ed25519",
    comment="my-key",
    output_path="~/.ssh/my_key"
)
```

### Command Line

```bash
# Execute command
python main.py server.example.com -u admin -c "ls -la" -p password

# Execute with key
python main.py server.example.com -u admin -c "whoami" -k ~/.ssh/id_rsa

# Upload file
python main.py server.example.com -u admin --upload local.txt /remote/path/ -k ~/.ssh/id_rsa

# Download file
python main.py server.example.com -u admin --download /remote/file.txt local.txt -p password

# Generate key
python main.py localhost --gen-key
```

## Configuration

Edit `skill.json` to customize:

```json
{
  "config": {
    "default_port": 22,
    "default_timeout": 30,
    "max_connections": 10,
    "key_types": ["rsa", "ed25519", "ecdsa"]
  }
}
```

## Key Management

```python
from main import SSHSkill

skill = SSHSkill()

# List existing keys
keys = skill.list_keys()
for key in keys:
    print(f"{key.key_type}: {key.fingerprint}")

# Generate new key
key_info = skill.generate_key(
    key_type="ed25519",
    comment="production-server",
    password="optional-passphrase"
)
```

## Sudo Execution

```python
result = ssh_command(
    hostname="server.example.com",
    command="apt-get update",
    username="admin",
    password="admin_pass",
    sudo=True,
    sudo_password="sudo_pass"
)
```

## Output Format

### Command Execution

```json
{
  "command": "ls -la",
  "stdout": "total 128\ndrwxr-xr-x 5 user group 4096 Jan 15 10:30 .",
  "stderr": "",
  "exit_code": 0,
  "execution_time": 0.523
}
```

### File Transfer

```json
{
  "local_path": "local_file.txt",
  "remote_path": "/remote/path/file.txt",
  "direction": "upload",
  "status": "success",
  "file_size": 1024,
  "transfer_time": 0.125
}
```

### Key Generation

```json
{
  "key_type": "ED25519",
  "fingerprint": "SHA256:abc123...",
  "comment": "my-key",
  "path": "/home/user/.ssh/id_ed25519",
  "size": 256
}
```

## Testing

```bash
python -m pytest tests/
```

## Security Notes

- Always use key-based authentication when possible
- Protect private keys with passphrases
- Use SSH agent for key management
- Regularly rotate SSH keys
- Monitor authorized_keys files

## License

MIT License - See LICENSE file
