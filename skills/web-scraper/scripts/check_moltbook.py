#!/usr/bin/env python3
"""
Kbot Moltbook Checker
Check Moltbook profile for new replies
"""

import sys
import json
import re
from datetime import datetime

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("[ERROR] pip install requests beautifulsoup4")
    sys.exit(1)

PROFILE_URL = "https://www.moltbook.com/u/kbot-windows"
CACHE_FILE = r"D:\kimi\memory\cache\moltbook_last_check.json"


def fetch_profile():
    """Fetch Moltbook profile page"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    
    try:
        response = requests.get(PROFILE_URL, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"[ERROR] Failed to fetch profile: {e}")
        return None


def extract_posts(html):
    """Extract posts and replies from profile page"""
    soup = BeautifulSoup(html, 'html.parser')
    
    posts = []
    
    # Try to find post elements (adjust selectors based on actual page structure)
    # Common patterns for social sites:
    post_selectors = [
        '[data-testid="post"]',
        '.post',
        '.tweet',
        'article',
        '[class*="post"]',
        '[class*="content"]',
    ]
    
    for selector in post_selectors:
        elements = soup.select(selector)
        if elements:
            for el in elements[:5]:  # Check first 5 posts
                text = el.get_text(strip=True)
                if text and len(text) > 20:
                    posts.append({
                        "text": text[:500],
                        "has_replies": "reply" in text.lower() or "comment" in text.lower(),
                    })
            break
    
    # If no structured posts found, extract all text
    if not posts:
        text = soup.get_text(separator='\n', strip=True)
        # Look for poll-related content
        if "payment" in text.lower() or "chain" in text.lower() or "base" in text.lower():
            posts.append({"text": text[:2000], "has_replies": True})
    
    return posts


def load_cache():
    """Load last check data"""
    import os
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"last_content": "", "check_count": 0}


def save_cache(content):
    """Save check data"""
    import os
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    data = {
        "last_content": content[:1000],
        "last_check": datetime.now().isoformat(),
        "check_count": load_cache().get("check_count", 0) + 1,
    }
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def analyze_poll_results(text):
    """Try to extract poll results from text"""
    results = {
        "base_mentions": len(re.findall(r'\bbase\b', text, re.IGNORECASE)),
        "solana_mentions": len(re.findall(r'\bsolana\b', text, re.IGNORECASE)),
        "ethereum_mentions": len(re.findall(r'\beth(?:ereum)?\b', text, re.IGNORECASE)),
        "other_mentions": len(re.findall(r'\bother\b', text, re.IGNORECASE)),
    }
    return results


def main():
    print("=" * 60)
    print("Kbot Moltbook Profile Checker")
    print("=" * 60)
    print(f"Checking: {PROFILE_URL}")
    print(f"Time: {datetime.now()}")
    print()
    
    html = fetch_profile()
    if not html:
        print("[FAILED] Could not fetch profile")
        sys.exit(1)
    
    print(f"[OK] Page fetched ({len(html)} bytes)")
    
    # Extract posts
    posts = extract_posts(html)
    print(f"[INFO] Found {len(posts)} potential posts")
    print()
    
    # Display content
    for i, post in enumerate(posts, 1):
        print(f"--- Post {i} ---")
        print(post["text"][:800])
        if post.get("has_replies"):
            print("[Note: May have replies]")
        print()
    
    # Analyze for poll results
    full_text = " ".join([p["text"] for p in posts])
    results = analyze_poll_results(full_text)
    
    print("--- Poll Analysis ---")
    print(f"Base mentions: {results['base_mentions']}")
    print(f"Solana mentions: {results['solana_mentions']}")
    print(f"Ethereum mentions: {results['ethereum_mentions']}")
    print(f"Other mentions: {results['other_mentions']}")
    print()
    
    # Recommendation
    if results['base_mentions'] > results['solana_mentions']:
        print("[RECOMMENDATION] Base is preferred")
    elif results['solana_mentions'] > results['base_mentions']:
        print("[RECOMMENDATION] Solana is preferred")
    else:
        print("[RECOMMENDATION] Tie or no clear preference - create both")
    
    # Save cache
    save_cache(full_text)
    print()
    print(f"[OK] Check complete. Total checks: {load_cache()['check_count']}")


if __name__ == "__main__":
    main()
