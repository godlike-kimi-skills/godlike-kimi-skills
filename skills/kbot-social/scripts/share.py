#!/usr/bin/env python3
"""
Kbot Moltbook Share
Share a discovery or update to the Moltbook network.
Usage: python share.py "Your message here"
"""

import json
import urllib.request
import urllib.error
import sys
import os

MOLTBOOK_API = "https://www.moltbook.com/api/v1"
API_KEY_FILE = r"D:\kimi\memory\state\moltbook_api_key.txt"


def get_api_key():
    """Read API key from secure storage."""
    try:
        with open(API_KEY_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print("[ERROR] API key not found.")
        return None


def share_post(content, post_type="thought"):
    """Share a post to Moltbook."""
    api_key = get_api_key()
    if not api_key:
        return False
    
    data = json.dumps({
        "content": content,
        "type": post_type
    }, ensure_ascii=False).encode('utf-8')
    
    try:
        req = urllib.request.Request(
            f"{MOLTBOOK_API}/posts",
            data=data,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "Kbot/1.0"
            },
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"[OK] Posted successfully!")
            print(f"Post ID: {result.get('id', 'N/A')}")
            return True
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"[ERROR] HTTP {e.code}: {error_body}")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python share.py \"Your message here\"")
        print("   or: python share.py --file path/to/content.txt")
        sys.exit(1)
    
    if sys.argv[1] == '--file':
        if len(sys.argv) < 3:
            print("[ERROR] Please provide a file path")
            sys.exit(1)
        try:
            with open(sys.argv[2], 'r') as f:
                content = f.read().strip()
        except FileNotFoundError:
            print(f"[ERROR] File not found: {sys.argv[2]}")
            sys.exit(1)
    else:
        content = sys.argv[1]
    
    # Limit content length (Moltbook likely has limits)
    if len(content) > 1000:
        content = content[:997] + "..."
        print("[WARNING] Content truncated to 1000 chars")
    
    print("=" * 60)
    print("Sharing to Moltbook...")
    print("=" * 60)
    print(f"Content: {content[:80]}...")
    
    if share_post(content):
        # Play success sound
        os.system('powershell -c "[console]::Beep(1000,200)"')
    else:
        os.system('powershell -c "[console]::Beep(800,300)"')
        sys.exit(1)


if __name__ == "__main__":
    main()
