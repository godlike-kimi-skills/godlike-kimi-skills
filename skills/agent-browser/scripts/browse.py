#!/usr/bin/env python3
"""Web Browser Implementation"""
import sys, json, urllib.request, ssl
from urllib.parse import urlparse

def browse(url, timeout=30):
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as response:
            content = response.read().decode('utf-8', errors='ignore')
            return {
                "url": url,
                "status": response.status,
                "content_length": len(content),
                "content_preview": content[:2000],
                "headers": dict(response.headers)
            }
    except Exception as e:
        return {"error": str(e), "url": url}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python browse.py <url>")
        sys.exit(1)
    print(json.dumps(browse(sys.argv[1]), indent=2, ensure_ascii=False))
