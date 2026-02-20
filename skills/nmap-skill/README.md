# nmap-skill

Nmap port scanning tool with service detection and OS fingerprinting capabilities.

Use when scanning networks, managing remote servers, or when user mentions 'SSH', 'DNS', 'network'.

## Features

- **Port Scanning**: TCP SYN, TCP Connect, UDP scanning
- **Service Detection**: Version detection and banner grabbing
- **OS Fingerprinting**: Operating system identification
- **Script Scanning**: NSE script support
- **Multiple Output Formats**: JSON, XML parsing
- **Scan Intensity Levels**: Quick, Normal, Intensive, Paranoid

## Installation

```bash
pip install -r requirements.txt
```

Requires `nmap` to be installed on the system:
- Ubuntu/Debian: `sudo apt-get install nmap`
- macOS: `brew install nmap`
- Windows: Download from https://nmap.org/download.html

## Usage

### As a Skill

```python
from main import scan, quick_scan, comprehensive_scan

# Basic scan
result = scan("192.168.1.1")

# Quick scan of top ports
result = quick_scan("example.com", ports="top-100")

# Comprehensive scan
result = comprehensive_scan("192.168.1.1")
```

### Command Line

```bash
# Basic scan
python main.py 192.168.1.1

# Scan specific ports
python main.py 192.168.1.1 -p 80,443,8080

# Service detection scan
python main.py 192.168.1.1 --service

# OS detection (requires root)
python main.py 192.168.1.1 --os
```

### Advanced Options

```python
from main import NmapSkill

skill = NmapSkill()

# Custom scan
result = skill.scan(
    target="192.168.1.0/24",
    ports="1-65535",
    scan_type="tcp_syn",
    intensity="intensive",
    service_detection=True,
    os_detection=True,
    script_scan="vuln"
)
```

## Configuration

Edit `skill.json` to customize:

```json
{
  "config": {
    "default_ports": "1-1000",
    "timeout": 300,
    "max_retries": 2
  }
}
```

## Scan Types

| Type | Description |
|------|-------------|
| tcp_syn | SYN stealth scan (requires root) |
| tcp_connect | TCP connect scan |
| udp | UDP scan |
| ack | ACK scan |

## Output Format

```json
{
  "success": true,
  "target": "192.168.1.1",
  "hosts_up": 1,
  "total_hosts": 1,
  "scan_time": 15.3,
  "results": [
    {
      "host": "192.168.1.1",
      "state": "up",
      "ports": [
        {
          "port": "80",
          "protocol": "tcp",
          "state": "open",
          "service": {
            "name": "http",
            "product": "nginx",
            "version": "1.18.0"
          }
        }
      ]
    }
  ]
}
```

## Testing

```bash
python -m pytest tests/
```

## License

MIT License - See LICENSE file
