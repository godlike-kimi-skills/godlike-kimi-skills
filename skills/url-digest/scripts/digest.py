#!/usr/bin/env python3
"""URL Digest Tool - Extract and summarize web content"""

import argparse
import json
import urllib.request
import urllib.error
from datetime import datetime
from typing import Dict, Optional


def fetch_url(url: str) -> Dict:
    """Fetch content from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8', errors='ignore')
            return {
                'url': url,
                'status': response.status,
                'content_length': len(html),
                'content': html[:5000],
                'fetched_at': datetime.now().isoformat()
            }
    except urllib.error.URLError as e:
        return {'error': str(e), 'url': url}
    except Exception as e:
        return {'error': str(e), 'url': url}


def extract_metadata(html: str) -> Dict:
    """Extract metadata from HTML"""
    import re
    
    title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    title = title_match.group(1).strip() if title_match else 'Unknown'
    
    desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)', html, re.IGNORECASE)
    if not desc_match:
        desc_match = re.search(r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*name=["\']description["\']', html, re.IGNORECASE)
    description = desc_match.group(1) if desc_match else ''
    
    return {
        'title': title,
        'description': description
    }


def summarize(url: str, format_type: str = 'json') -> str:
    """Summarize URL content"""
    result = fetch_url(url)
    
    if 'error' in result:
        return json.dumps(result, indent=2)
    
    metadata = extract_metadata(result['content'])
    
    summary = {
        'url': url,
        'title': metadata['title'],
        'description': metadata['description'],
        'fetched_at': result['fetched_at'],
        'content_preview': result['content'][:500] + '...' if len(result['content']) > 500 else result['content']
    }
    
    if format_type == 'markdown':
        return f"""# {summary['title']}

**URL**: {url}
**Fetched**: {summary['fetched_at']}

## Description
{summary['description']}

## Content Preview
```
{summary['content_preview']}
```
"""
    else:
        return json.dumps(summary, indent=2, ensure_ascii=False)


def batch_process(file_path: str, output: str) -> None:
    """Process multiple URLs from file"""
    with open(file_path, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    results = []
    for url in urls:
        result = fetch_url(url)
        if 'content' in result:
            metadata = extract_metadata(result['content'])
            results.append({
                'url': url,
                'title': metadata['title'],
                'description': metadata['description']
            })
    
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Processed {len(results)} URLs, saved to {output}")


def main():
    parser = argparse.ArgumentParser(description='URL Digest Tool')
    subparsers = parser.add_subparsers(dest='command')
    
    sum_parser = subparsers.add_parser('summarize')
    sum_parser.add_argument('url')
    sum_parser.add_argument('--format', choices=['json', 'markdown'], default='json')
    
    batch_parser = subparsers.add_parser('batch')
    batch_parser.add_argument('--file', required=True)
    batch_parser.add_argument('--output', required=True)
    
    args = parser.parse_args()
    
    if args.command == 'summarize':
        print(summarize(args.url, args.format))
    elif args.command == 'batch':
        batch_process(args.file, args.output)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
