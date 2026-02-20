#!/usr/bin/env python3
"""
Nginx Skill Usage Examples
"""

import sys
sys.path.insert(0, '..')

from scripts.main import NginxManager, VirtualHostConfig, UpstreamConfig, ServerConfig, LocationConfig

def example_basic_vhost():
    """Create a basic virtual host"""
    nginx = NginxManager("/tmp/nginx-test")
    
    config = VirtualHostConfig(
        server_name="mywebsite.com",
        port=80,
        document_root="/var/www/mywebsite",
        index_files="index.html index.php"
    )
    
    path = nginx.create_vhost(config, enable=True)
    print(f"Created virtual host: {path}")
    return path

def example_ssl_vhost():
    """Create SSL-enabled virtual host"""
    nginx = NginxManager("/tmp/nginx-test")
    
    config = VirtualHostConfig(
        server_name="secure.example.com",
        port=443,
        document_root="/var/www/secure",
        ssl_enabled=True,
        ssl_cert_path="/etc/ssl/certs/example.com.crt",
        ssl_key_path="/etc/ssl/private/example.com.key",
        gzip_enabled=True
    )
    
    path = nginx.create_vhost(config)
    print(f"Created SSL virtual host: {path}")
    return path

def example_reverse_proxy():
    """Create reverse proxy configuration"""
    nginx = NginxManager("/tmp/nginx-test")
    
    custom_locations = [
        LocationConfig("/api/", "proxy_pass http://api_backend;"),
        LocationConfig("/static/", "alias /var/www/static/;")
    ]
    
    config = VirtualHostConfig(
        server_name="api.example.com",
        port=80,
        proxy_enabled=True,
        proxy_pass="http://localhost:3000",
        custom_locations=custom_locations
    )
    
    path = nginx.create_vhost(config)
    print(f"Created reverse proxy: {path}")
    return path

def example_load_balancer():
    """Create load balancer configuration"""
    nginx = NginxManager("/tmp/nginx-test")
    
    servers = [
        ServerConfig("192.168.1.10:8080", weight=5),
        ServerConfig("192.168.1.11:8080", weight=5),
        ServerConfig("192.168.1.12:8080", weight=1, backup=True)
    ]
    
    upstream = UpstreamConfig(
        upstream_name="backend_servers",
        upstream_servers=servers,
        load_balance_method="least_conn",
        keepalive_connections=64
    )
    
    path = nginx.create_upstream(upstream)
    print(f"Created upstream: {path}")
    return path

def example_site_management():
    """Manage sites (enable/disable/delete)"""
    nginx = NginxManager("/tmp/nginx-test")
    
    # List all sites
    sites = nginx.list_sites()
    print("Available sites:", sites["available"])
    print("Enabled sites:", sites["enabled"])
    
    # Enable a site
    nginx.enable_site("mywebsite.com")
    print("Enabled mywebsite.com")
    
    # Disable a site
    nginx.disable_site("mywebsite.com")
    print("Disabled mywebsite.com")

if __name__ == "__main__":
    print("=" * 60)
    print("Nginx Skill Examples")
    print("=" * 60)
    
    print("\n1. Basic Virtual Host:")
    example_basic_vhost()
    
    print("\n2. SSL Virtual Host:")
    example_ssl_vhost()
    
    print("\n3. Reverse Proxy:")
    example_reverse_proxy()
    
    print("\n4. Load Balancer:")
    example_load_balancer()
    
    print("\n5. Site Management:")
    example_site_management()
