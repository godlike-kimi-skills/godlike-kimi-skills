# nmap-skill

Nmap port scanning tool with service detection and OS fingerprinting capabilities.

Use when scanning networks, managing remote servers, or when user mentions 'SSH', 'DNS', 'network'.

## Overview

This skill provides network discovery and security auditing capabilities through the power of Nmap. It supports various scan types, service detection, and operating system fingerprinting.

## Triggers

- "scan network"
- "port scan"
- "nmap"
- "check ports"
- "service detection"
- "network discovery"

## Functions

### scan(target, **kwargs)

Perform a port scan on the specified target.

**Parameters:**
- `target` (str): IP address, hostname, or CIDR range
- `ports` (str): Port specification (e.g., "80,443" or "1-1000")
- `scan_type` (str): Type of scan - "tcp_syn", "tcp_connect", "udp"
- `intensity` (str): "quick", "normal", "intensive", "paranoid"
- `service_detection` (bool): Enable service version detection
- `os_detection` (bool): Enable OS fingerprinting
- `script_scan` (str): NSE script to run

**Returns:**
Dictionary with scan results including open ports, services, and OS information.

### quick_scan(target, ports="top-100")

Quick scan of top 100 common ports.

**Parameters:**
- `target` (str): Target to scan
- `ports` (str): "top-100" or custom port specification

### comprehensive_scan(target)

Full comprehensive scan of all ports with all features enabled.

**Parameters:**
- `target` (str): Target to scan

## Examples

```python
# Scan a single host
scan("192.168.1.1")

# Scan with service detection
scan("example.com", service_detection=True)

# Quick scan
quick_scan("192.168.1.0/24")

# Full port scan with OS detection
comprehensive_scan("target.com")
```

## Requirements

- Python 3.8+
- nmap installed on system
- Root privileges for certain scan types

## Safety Notice

⚠️ Only scan networks you have permission to scan. Unauthorized scanning may violate laws and policies.
