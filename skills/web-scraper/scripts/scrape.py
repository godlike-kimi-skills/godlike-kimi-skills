#!/usr/bin/env python3
"""
Kbot Web Scraper
Lightweight scraping for checking web pages
"""

import argparse
import json
import sys
import hashlib
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("[ERROR] Need to install: pip install requests beautifulsoup4")
    sys.exit(1)

CACHE_DIR = r"D:\kimi\memory\cache\scrapes"


def fetch_page(url, headers=None):
    """Fetch page content"""
    default_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    if headers:
        default_headers.update(headers)
    
    try:
        response = requests.get(url, headers=default_headers, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"[ERROR] Failed to fetch {url}: {e}")
        return None


def parse_content(html, selector=None):
    """Parse HTML content"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    if selector:
        elements = soup.select(selector)
        return "\n".join([el.get_text(strip=True) for el in elements])
    else:
        # Get main content
        text = soup.get_text(separator='\n', strip=True)
        # Clean up empty lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return "\n".join(lines[:100])  # Limit to first 100 lines


def get_cache_path(url):
    """Get cache file path for URL"""
    import os
    os.makedirs(CACHE_DIR, exist_ok=True)
    url_hash = hashlib.md5(url.encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"{url_hash}.json")


def load_cache(url):
    """Load cached content"""
    import os
    cache_path = get_cache_path(url)
    if os.path.exists(cache_path):
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def save_cache(url, content):
    """Save content to cache"""
    cache_path = get_cache_path(url)
    data = {
        "url": url,
        "content": content,
        "hash": hashlib.md5(content.encode()).hexdigest(),
        "timestamp": json.dumps({}),  # Will be added
    }
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def check_changes(url, new_content):
    """Check if content changed"""
    cache = load_cache(url)
    if not cache:
        return True, "New page"
    
    new_hash = hashlib.md5(new_content.encode()).hexdigest()
    if new_hash != cache.get("hash"):
        return True, "Content changed"
    return False, "No changes"


def main():
    parser = argparse.ArgumentParser(description="Kbot Web Scraper")
    parser.add_argument("--url", required=True, help="URL to scrape")
    parser.add_argument("--selector", help="CSS selector to extract")
    parser.add_argument("--compare", action="store_true", help="Check for changes")
    parser.add_argument("--save", action="store_true", help="Save to cache")
    
    args = parser.parse_args()
    
    print(f"[INFO] Fetching {args.url}...")
    html = fetch_page(args.url)
    if not html:
        sys.exit(1)
    
    print(f"[INFO] Parsing content...")
    content = parse_content(html, args.selector)
    
    if args.compare:
        changed, message = check_changes(args.url, content)
        print(f"[RESULT] {message}")
        if changed:
            print("\n--- NEW CONTENT ---")
            print(content[:2000])  # Show first 2000 chars
    else:
        print("\n--- CONTENT ---")
        print(content[:3000])  # Show first 3000 chars
    
    if args.save or args.compare:
        save_cache(args.url, content)
        print(f"\n[INFO] Saved to cache")


if __name__ == "__main__":
    main()
