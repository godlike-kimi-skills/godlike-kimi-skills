#!/usr/bin/env python3
"""
Nginx Configuration Management Skill
Supports: virtual hosts, SSL, load balancing, reverse proxy
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from jinja2 import Template

# ============================================================================
# Configuration Templates
# ============================================================================

NGINX_VHOST_TEMPLATE = '''
server {
    listen {{ port }};
    listen [::]:{{ port }};
    server_name {{ server_name }};
    
    root {{ document_root }};
    index {{ index_files }};
    
    # Logging
    access_log /var/log/nginx/{{ server_name }}_access.log;
    error_log /var/log/nginx/{{ server_name }}_error.log;
    
    {% if ssl_enabled %}
    # SSL Configuration
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    ssl_certificate {{ ssl_cert_path }};
    ssl_certificate_key {{ ssl_key_path }};
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    {% endif %}
    
    {% if gzip_enabled %}
    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
    {% endif %}
    
    location / {
        try_files $uri $uri/ =404;
        {% if proxy_enabled %}
        proxy_pass {{ proxy_pass }};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        {% endif %}
    }
    
    {% for location in custom_locations %}
    location {{ location.path }} {
        {{ location.directive }}
    }
    {% endfor %}
}
'''

NGINX_UPSTREAM_TEMPLATE = '''
upstream {{ upstream_name }} {
    {% for server in upstream_servers %}
    server {{ server.address }} weight={{ server.weight }} {{ 'backup' if server.backup else '' }};
    {% endfor %}
    
    {% if load_balance_method == 'least_conn' %}
    least_conn;
    {% elif load_balance_method == 'ip_hash' %}
    ip_hash;
    {% endif %}
    
    keepalive {{ keepalive_connections }};
}
'''

# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class ServerConfig:
    """Server configuration for upstream"""
    address: str
    weight: int = 1
    backup: bool = False

@dataclass
class LocationConfig:
    """Location block configuration"""
    path: str
    directive: str

@dataclass
class VirtualHostConfig:
    """Virtual host configuration"""
    server_name: str
    port: int = 80
    document_root: str = "/var/www/html"
    index_files: str = "index.html index.php"
    ssl_enabled: bool = False
    ssl_cert_path: str = ""
    ssl_key_path: str = ""
    gzip_enabled: bool = True
    proxy_enabled: bool = False
    proxy_pass: str = ""
    custom_locations: List[LocationConfig] = None
    
    def __post_init__(self):
        if self.custom_locations is None:
            self.custom_locations = []

@dataclass
class UpstreamConfig:
    """Upstream/load balancer configuration"""
    upstream_name: str
    upstream_servers: List[ServerConfig]
    load_balance_method: str = "round_robin"  # round_robin, least_conn, ip_hash
    keepalive_connections: int = 32

# ============================================================================
# Nginx Manager Class
# ============================================================================

class NginxManager:
    """Main class for managing Nginx configurations"""
    
    def __init__(self, config_dir: str = "/etc/nginx"):
        self.config_dir = Path(config_dir)
        self.sites_available = self.config_dir / "sites-available"
        self.sites_enabled = self.config_dir / "sites-enabled"
        self.conf_d = self.config_dir / "conf.d"
        
    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist"""
        for directory in [self.sites_available, self.sites_enabled, self.conf_d]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def generate_vhost_config(self, config: VirtualHostConfig) -> str:
        """Generate virtual host configuration from template"""
        template = Template(NGINX_VHOST_TEMPLATE)
        return template.render(
            server_name=config.server_name,
            port=config.port,
            document_root=config.document_root,
            index_files=config.index_files,
            ssl_enabled=config.ssl_enabled,
            ssl_cert_path=config.ssl_cert_path,
            ssl_key_path=config.ssl_key_path,
            gzip_enabled=config.gzip_enabled,
            proxy_enabled=config.proxy_enabled,
            proxy_pass=config.proxy_pass,
            custom_locations=[asdict(loc) for loc in config.custom_locations]
        )
    
    def generate_upstream_config(self, config: UpstreamConfig) -> str:
        """Generate upstream/load balancer configuration"""
        template = Template(NGINX_UPSTREAM_TEMPLATE)
        return template.render(
            upstream_name=config.upstream_name,
            upstream_servers=[asdict(srv) for srv in config.upstream_servers],
            load_balance_method=config.load_balance_method,
            keepalive_connections=config.keepalive_connections
        )
    
    def create_vhost(self, config: VirtualHostConfig, enable: bool = True) -> str:
        """Create a new virtual host configuration"""
        self.ensure_directories()
        
        config_content = self.generate_vhost_config(config)
        config_file = self.sites_available / f"{config.server_name}.conf"
        
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        if enable:
            self.enable_site(config.server_name)
        
        return str(config_file)
    
    def create_upstream(self, config: UpstreamConfig) -> str:
        """Create upstream configuration"""
        self.ensure_directories()
        
        config_content = self.generate_upstream_config(config)
        config_file = self.conf_d / f"upstream_{config.upstream_name}.conf"
        
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        return str(config_file)
    
    def enable_site(self, server_name: str) -> bool:
        """Enable a site by creating symlink"""
        available = self.sites_available / f"{server_name}.conf"
        enabled = self.sites_enabled / f"{server_name}.conf"
        
        if not available.exists():
            print(f"Error: Configuration for {server_name} not found")
            return False
        
        if enabled.exists() or enabled.is_symlink():
            enabled.unlink()
        
        enabled.symlink_to(available)
        return True
    
    def disable_site(self, server_name: str) -> bool:
        """Disable a site by removing symlink"""
        enabled = self.sites_enabled / f"{server_name}.conf"
        
        if enabled.exists() or enabled.is_symlink():
            enabled.unlink()
            return True
        return False
    
    def delete_site(self, server_name: str) -> bool:
        """Delete a site configuration"""
        available = self.sites_available / f"{server_name}.conf"
        self.disable_site(server_name)
        
        if available.exists():
            available.unlink()
            return True
        return False
    
    def list_sites(self) -> Dict[str, List[str]]:
        """List all sites and their status"""
        available = [f.stem for f in self.sites_available.glob("*.conf")]
        enabled = [f.stem for f in self.sites_enabled.glob("*.conf")]
        
        return {
            "available": available,
            "enabled": enabled,
            "disabled": list(set(available) - set(enabled))
        }
    
    def test_config(self) -> Tuple[bool, str]:
        """Test Nginx configuration syntax"""
        try:
            result = subprocess.run(
                ["nginx", "-t"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0, result.stderr
        except FileNotFoundError:
            return False, "nginx command not found"
    
    def reload_nginx(self) -> Tuple[bool, str]:
        """Reload Nginx configuration"""
        try:
            result = subprocess.run(
                ["nginx", "-s", "reload"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0, result.stderr
        except FileNotFoundError:
            return False, "nginx command not found"
    
    def create_ssl_vhost(self, server_name: str, document_root: str,
                         cert_path: str, key_path: str, 
                         redirect_http: bool = True) -> str:
        """Create SSL-enabled virtual host"""
        config = VirtualHostConfig(
            server_name=server_name,
            port=80 if redirect_http else 443,
            document_root=document_root,
            ssl_enabled=True,
            ssl_cert_path=cert_path,
            ssl_key_path=key_path
        )
        return self.create_vhost(config)
    
    def create_reverse_proxy(self, server_name: str, upstream_url: str,
                             locations: List[Tuple[str, str]] = None) -> str:
        """Create reverse proxy configuration"""
        custom_locs = []
        if locations:
            for path, directive in locations:
                custom_locs.append(LocationConfig(path=path, directive=directive))
        
        config = VirtualHostConfig(
            server_name=server_name,
            proxy_enabled=True,
            proxy_pass=upstream_url,
            custom_locations=custom_locs
        )
        return self.create_vhost(config)

# ============================================================================
# CLI Interface
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Nginx Configuration Manager")
    parser.add_argument("--config-dir", default="/etc/nginx", help="Nginx config directory")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create vhost command
    create_parser = subparsers.add_parser("create-vhost", help="Create virtual host")
    create_parser.add_argument("--server-name", required=True, help="Server name")
    create_parser.add_argument("--document-root", default="/var/www/html", help="Document root")
    create_parser.add_argument("--port", type=int, default=80, help="Port number")
    create_parser.add_argument("--ssl", action="store_true", help="Enable SSL")
    create_parser.add_argument("--ssl-cert", help="SSL certificate path")
    create_parser.add_argument("--ssl-key", help="SSL key path")
    create_parser.add_argument("--proxy", help="Proxy pass URL")
    
    # Create upstream command
    upstream_parser = subparsers.add_parser("create-upstream", help="Create upstream")
    upstream_parser.add_argument("--name", required=True, help="Upstream name")
    upstream_parser.add_argument("--servers", required=True, help="Servers (host:port,weight)")
    upstream_parser.add_argument("--method", default="round_robin", 
                                  choices=["round_robin", "least_conn", "ip_hash"])
    
    # Site management
    subparsers.add_parser("list", help="List all sites")
    enable_parser = subparsers.add_parser("enable", help="Enable site")
    enable_parser.add_argument("server_name", help="Server name to enable")
    disable_parser = subparsers.add_parser("disable", help="Disable site")
    disable_parser.add_argument("server_name", help="Server name to disable")
    delete_parser = subparsers.add_parser("delete", help="Delete site")
    delete_parser.add_argument("server_name", help="Server name to delete")
    
    # Nginx control
    subparsers.add_parser("test", help="Test configuration")
    subparsers.add_parser("reload", help="Reload Nginx")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = NginxManager(args.config_dir)
    
    if args.command == "create-vhost":
        config = VirtualHostConfig(
            server_name=args.server_name,
            port=args.port,
            document_root=args.document_root,
            ssl_enabled=args.ssl,
            ssl_cert_path=args.ssl_cert or "",
            ssl_key_path=args.ssl_key or "",
            proxy_enabled=args.proxy is not None,
            proxy_pass=args.proxy or ""
        )
        path = manager.create_vhost(config)
        print(f"Created virtual host: {path}")
    
    elif args.command == "create-upstream":
        servers = []
        for srv_str in args.servers.split(","):
            parts = srv_str.split(":")
            if len(parts) >= 2:
                weight = int(parts[2]) if len(parts) > 2 else 1
                servers.append(ServerConfig(address=f"{parts[0]}:{parts[1]}", weight=weight))
        
        config = UpstreamConfig(
            upstream_name=args.name,
            upstream_servers=servers,
            load_balance_method=args.method
        )
        path = manager.create_upstream(config)
        print(f"Created upstream: {path}")
    
    elif args.command == "list":
        sites = manager.list_sites()
        print("Enabled sites:", ", ".join(sites["enabled"]) or "None")
        print("Disabled sites:", ", ".join(sites["disabled"]) or "None")
    
    elif args.command == "enable":
        if manager.enable_site(args.server_name):
            print(f"Enabled {args.server_name}")
    
    elif args.command == "disable":
        if manager.disable_site(args.server_name):
            print(f"Disabled {args.server_name}")
    
    elif args.command == "delete":
        if manager.delete_site(args.server_name):
            print(f"Deleted {args.server_name}")
    
    elif args.command == "test":
        success, msg = manager.test_config()
        print("Configuration valid" if success else f"Error: {msg}")
    
    elif args.command == "reload":
        success, msg = manager.reload_nginx()
        print("Reloaded" if success else f"Error: {msg}")

if __name__ == "__main__":
    main()
