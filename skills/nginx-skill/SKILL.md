---
name: nginx-skill
description: Nginx configuration management for virtual hosts, SSL certificates, load balancing, and reverse proxy. Use when setting up web servers, managing multiple domains, configuring HTTPS, or implementing load balancers. Handles Nginx config generation, site enable/disable, upstream configuration, and syntax validation.
---

# Nginx Configuration Skill

## Use When
- Setting up virtual hosts for multiple domains
- Configuring SSL/HTTPS certificates
- Implementing load balancers with upstream servers
- Creating reverse proxy configurations
- Managing Nginx site configurations
- Testing Nginx configuration syntax
- Reloading Nginx services

## Out of Scope
- Installing Nginx (assumes already installed)
- System-level Nginx service management (systemd)
- Complex Lua scripting with OpenResty
- Real-time log monitoring
- Advanced rate limiting configurations
- Web Application Firewall (WAF) rules

## Quick Start

```python
from scripts.main import NginxManager, VirtualHostConfig

# Initialize manager
nginx = NginxManager("/etc/nginx")

# Create virtual host
config = VirtualHostConfig(
    server_name="example.com",
    port=80,
    document_root="/var/www/example.com"
)
nginx.create_vhost(config)

# Enable site
nginx.enable_site("example.com")

# Test and reload
nginx.test_config()
nginx.reload_nginx()
```

## Core Features

### Virtual Host Management
- Create/delete virtual host configurations
- Enable/disable sites
- Custom location blocks
- Gzip compression settings

### SSL/HTTPS Configuration
- SSL certificate and key paths
- TLS version configuration
- Cipher suite selection
- HTTP to HTTPS redirects

### Load Balancing
- Upstream server definitions
- Weighted load balancing
- Backup servers
- Connection keepalive

## CLI Usage

```bash
# Create virtual host
python scripts/main.py create-vhost --server-name example.com --document-root /var/www/html

# Create SSL-enabled host
python scripts/main.py create-vhost --server-name secure.example.com --ssl --ssl-cert /path/to/cert.pem --ssl-key /path/to/key.pem

# Create reverse proxy
python scripts/main.py create-vhost --server-name api.example.com --proxy http://localhost:3000

# Create load balancer
python scripts/main.py create-upstream --name backend --servers "192.168.1.10:8080,1:192.168.1.11:8080,1" --method least_conn

# Manage sites
python scripts/main.py list
python scripts/main.py enable example.com
python scripts/main.py disable example.com
python scripts/main.py delete example.com

# Test and reload
python scripts/main.py test
python scripts/main.py reload
```

## Configuration Structure

```
/etc/nginx/
├── nginx.conf
├── sites-available/     # Virtual host configs
│   └── example.com.conf
├── sites-enabled/       # Symlinks to enabled sites
│   └── example.com.conf -> ../sites-available/example.com.conf
└── conf.d/             # Additional configurations
    └── upstream_backend.conf
```
