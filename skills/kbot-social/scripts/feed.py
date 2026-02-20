#!/usr/bin/env python3
"""
Kbot Moltbook Feed Reader
Read and display the latest posts from the Moltbook agent network.
"""

import json
import urllib.request
import urllib.error
import os

MOLTBOOK_API = "https://www.moltbook.com/api/v1"
API_KEY_FILE = r"D:\kimi\memory\state\moltbook_api_key.txt"


def get_api_key():
    """Read API key from secure storage."""
    try:
        with open(API_KEY_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print("[ERROR] API key not found. Run registration first.")
        return None


def fetch_feed():
    """Fetch the public feed from Moltbook."""
    try:
        # Public feed doesn't require auth
        req = urllib.request.Request(
            f"{MOLTBOOK_API}/feed",
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Kbot/1.0"
            }
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"[ERROR] HTTP {e.code}: {e.reason}")
        return None
    except Exception as e:
        print(f"[ERROR] {e}")
        return None


def fetch_my_feed():
    """Fetch Kbot's personal feed (requires auth)."""
    api_key = get_api_key()
    if not api_key:
        return None
    
    try:
        req = urllib.request.Request(
            f"{MOLTBOOK_API}/feed/me",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "Kbot/1.0"
            }
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"[ERROR] HTTP {e.code}: {e.reason}")
        return None
    except Exception as e:
        print(f"[ERROR] {e}")
        return None


def format_post(post):
    """Format a single post for display."""
    agent = post.get('agent', {}).get('name', 'Unknown')
    content = post.get('content', 'No content')
    created = post.get('created_at', '')
    karma = post.get('karma_score', 0)
    
    return f"""
[{created}] @{agent} (karma: {karma})
{content}
---"""


def main():
    print("=" * 60)
    print("Moltbook Feed Reader")
    print("=" * 60)
    
    # Try to fetch personal feed first
    print("\n[Fetching your feed...]")
    my_feed = fetch_my_feed()
    if my_feed:
        posts = my_feed.get('posts', [])
        if posts:
            print(f"\n--- Your Feed ({len(posts)} posts) ---")
            for post in posts:
                print(format_post(post))
        else:
            print("\nNo posts in your feed yet.")
    
    # Fetch public feed
    print("\n[Fetching public feed...]")
    feed = fetch_feed()
    if feed:
        posts = feed.get('posts', [])
        if posts:
            print(f"\n--- Public Feed ({len(posts)} posts) ---")
            for post in posts[:10]:  # Show top 10
                print(format_post(post))
        else:
            print("\nNo posts in public feed.")
    else:
        print("\nFailed to fetch public feed.")


if __name__ == "__main__":
    main()
