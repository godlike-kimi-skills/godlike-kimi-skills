# Nginx Configuration Guide

## Table of Contents
1. [Virtual Host Configuration](#virtual-host)
2. [SSL/HTTPS Setup](#ssl-https)
3. [Load Balancing](#load-balancing)
4. [Reverse Proxy](#reverse-proxy)
5. [Performance Tuning](#performance)

## Virtual Host <a name="virtual-host"></a>

### Basic Configuration
```nginx
server {
    listen 80;
    server_name example.com www.example.com;
    root /var/www/example.com;
    index index.html index.htm;
    
    location / {
        try_files $uri $uri/ =404;
    }
}
```

### Multiple Domains
```nginx
server {
    listen 80;
    server_name domain1.com domain2.com;
    root /var/www/multi-domain;
}
```

## SSL/HTTPS <a name="ssl-https"></a>

### Basic SSL Configuration
```nginx
server {
    listen 443 ssl http2;
    server_name secure.example.com;
    
    ssl_certificate /etc/ssl/certs/example.com.crt;
    ssl_certificate_key /etc/ssl/private/example.com.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers on;
}
```

### HTTP to HTTPS Redirect
```nginx
server {
    listen 80;
    server_name example.com;
    return 301 https://$server_name$request_uri;
}
```

## Load Balancing <a name="load-balancing"></a>

### Methods
- **round_robin** (default): Distributes requests evenly
- **least_conn**: Sends to server with fewest connections
- **ip_hash**: Uses client IP for sticky sessions

### Upstream Configuration
```nginx
upstream backend {
    least_conn;
    server 192.168.1.10:8080 weight=5;
    server 192.168.1.11:8080 weight=5;
    server 192.168.1.12:8080 backup;
    keepalive 32;
}
```

### Health Checks
```nginx
upstream backend {
    server 192.168.1.10:8080 max_fails=3 fail_timeout=30s;
    server 192.168.1.11:8080 max_fails=3 fail_timeout=30s;
}
```

## Reverse Proxy <a name="reverse-proxy"></a>

### Basic Proxy
```nginx
location / {
    proxy_pass http://localhost:3000;
    proxy_http_version 1.1;
    
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### WebSocket Support
```nginx
location /ws {
    proxy_pass http://localhost:3000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

## Performance <a name="performance"></a>

### Gzip Compression
```nginx
gzip on;
gzip_vary on;
gzip_proxied any;
gzip_comp_level 6;
gzip_types text/plain text/css text/xml application/json application/javascript;
```

### Client Caching
```nginx
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### Buffer Settings
```nginx
proxy_buffering on;
proxy_buffer_size 4k;
proxy_buffers 8 4k;
proxy_busy_buffers_size 8k;
```

## Common Issues

### Permission Denied
Ensure Nginx user has read access to document root:
```bash
chown -R www-data:www-data /var/www/html
chmod -R 755 /var/www/html
```

### Configuration Test
Always test before reloading:
```bash
nginx -t
nginx -s reload
```
