#!/usr/bin/env python3
"""
Brightdata Scraper
Advanced web scraping with proxy rotation and anti-detection
"""

import argparse
import json
import sys
import time
import random
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("[ERROR] pip install requests beautifulsoup4")
    sys.exit(1)

# Default headers to mimic real browser
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# Simple proxy rotation (free proxies - for demo only)
# In production, use Brightdata or similar paid service
FREE_PROXIES = []


def get_random_headers():
    """Generate random headers for each request"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    ]
    headers = DEFAULT_HEADERS.copy()
    headers["User-Agent"] = random.choice(user_agents)
    return headers


def scrape_with_retry(url, max_retries=3, delay=2, use_proxies=False):
    """
    Scrape URL with retry logic and anti-detection measures
    
    Args:
        url: URL to scrape
        max_retries: Number of retry attempts
        delay: Delay between retries (seconds)
        use_proxies: Whether to use proxy rotation
    
    Returns:
        dict with content, status, and metadata
    """
    for attempt in range(max_retries):
        try:
            # Random delay to avoid rate limiting
            if attempt > 0:
                sleep_time = delay * (attempt + 1) + random.uniform(0, 1)
                print(f"[INFO] Retrying in {sleep_time:.1f}s...")
                time.sleep(sleep_time)
            
            headers = get_random_headers()
            
            # Make request
            response = requests.get(
                url,
                headers=headers,
                timeout=30,
                allow_redirects=True,
            )
            
            # Check for blocks
            if response.status_code == 403:
                print(f"[WARNING] Attempt {attempt + 1}: Blocked (403)")
                continue
            elif response.status_code == 429:
                print(f"[WARNING] Attempt {attempt + 1}: Rate limited (429)")
                continue
            
            response.raise_for_status()
            
            # Parse content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
            
            # Extract text
            text = soup.get_text(separator='\n', strip=True)
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            return {
                "url": url,
                "status": response.status_code,
                "title": soup.title.string if soup.title else "",
                "content": "\n".join(lines[:200]),  # Limit lines
                "success": True,
                "attempts": attempt + 1,
            }
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                return {
                    "url": url,
                    "error": str(e),
                    "success": False,
                    "attempts": attempt + 1,
                }
    
    return {
        "url": url,
        "error": "Max retries exceeded",
        "success": False,
        "attempts": max_retries,
    }


def batch_scrape(urls, output_file=None):
    """Scrape multiple URLs"""
    results = []
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Scraping: {url}")
        result = scrape_with_retry(url.strip())
        results.append(result)
        
        # Delay between requests
        if i < len(urls):
            delay = random.uniform(2, 5)
            print(f"[INFO] Waiting {delay:.1f}s before next request...")
            time.sleep(delay)
    
    # Save results
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n[OK] Results saved to {output_file}")
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Brightdata-style Scraper")
    parser.add_argument("url", help="URL to scrape or file containing URLs")
    parser.add_argument("--batch", action="store_true", help="Treat URL as file with URLs")
    parser.add_argument("--proxies", action="store_true", help="Use proxy rotation")
    parser.add_argument("--retries", type=int, default=3, help="Max retries")
    parser.add_argument("--output", help="Output JSON file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    if args.batch:
        # Read URLs from file
        with open(args.url, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        results = batch_scrape(urls, args.output)
        
        # Summary
        success_count = sum(1 for r in results if r["success"])
        print(f"\n=== Summary ===")
        print(f"Total: {len(results)}")
        print(f"Success: {success_count}")
        print(f"Failed: {len(results) - success_count}")
        
    else:
        # Single URL
        result = scrape_with_retry(
            args.url,
            max_retries=args.retries,
            use_proxies=args.proxies,
        )
        
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            if result["success"]:
                print(f"\nTitle: {result.get('title', 'N/A')}")
                print(f"Status: {result['status']}")
                print(f"Attempts: {result['attempts']}")
                print("\n" + "="*60)
                print(result["content"][:3000])
            else:
                print(f"[FAILED] {result.get('error')}")
                sys.exit(1)


if __name__ == "__main__":
    main()
