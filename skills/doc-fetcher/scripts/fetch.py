#!/usr/bin/env python3
"""
Fetch and summarize web documentation.
Usage: fetch.py <url> [--summary] [--output <file>]
"""

import sys
import re
import argparse
import urllib.request
import urllib.error
from urllib.parse import urlparse
import html


def fetch_url(url, timeout=30):
    """Fetch content from a URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0'
        }
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request, timeout=timeout) as response:
            content_type = response.headers.get('Content-Type', '')
            charset = 'utf-8'
            if 'charset=' in content_type:
                charset = content_type.split('charset=')[-1].split(';')[0]
            
            content = response.read().decode(charset, errors='ignore')
            return content
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error fetching URL: {e}", file=sys.stderr)
        return None


def extract_text(html_content):
    """Extract readable text from HTML."""
    # Remove script and style elements
    text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Extract title
    title_match = re.search(r'<title[^>]*>(.*?)</title>', text, re.IGNORECASE | re.DOTALL)
    title = title_match.group(1).strip() if title_match else "No Title"
    
    # Try to extract main content
    main_content = ""
    
    # Look for article, main, or content div
    patterns = [
        r'<article[^>]*>(.*?)</article>',
        r'<main[^>]*>(.*?)</main>',
        r'<div[^>]*class=["\'][^"\']*content[^"\']*["\'][^>]*>(.*?)</div>',
        r'<div[^>]*class=["\'][^"\']*main[^"\']*["\'][^>]*>(.*?)</div>',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            main_content = match.group(1)
            break
    
    # If no main content found, use body
    if not main_content:
        body_match = re.search(r'<body[^>]*>(.*?)</body>', text, re.DOTALL | re.IGNORECASE)
        if body_match:
            main_content = body_match.group(1)
    
    # Remove remaining HTML tags
    text = re.sub(r'<[^>]+>', ' ', main_content)
    
    # Decode HTML entities
    text = html.unescape(text)
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return title, text


def summarize_text(text, max_length=500):
    """Create a summary of the text."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    summary = []
    current_length = 0
    
    for sentence in sentences[:5]:  # Take first 5 sentences
        if current_length + len(sentence) > max_length:
            break
        summary.append(sentence)
        current_length += len(sentence)
    
    return ' '.join(summary)


def extract_code_blocks(text):
    """Extract code blocks from HTML."""
    code_blocks = []
    
    # Find pre/code blocks
    pattern = r'<pre[^>]*>(.*?)</pre>'
    matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
    
    for match in matches:
        # Remove inner code tags
        code = re.sub(r'<code[^>]*>(.*?)</code>', r'\1', match, flags=re.DOTALL | re.IGNORECASE)
        code = re.sub(r'<[^>]+>', '', code)
        code = html.unescape(code)
        if code.strip():
            code_blocks.append(code.strip())
    
    return code_blocks


def format_as_markdown(title, text, url, code_blocks=None):
    """Format content as Markdown."""
    md = f"# {title}\n\n"
    md += f"**Source:** {url}\n\n"
    md += "---\n\n"
    
    # Add main content
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    for para in paragraphs[:20]:  # Limit to 20 paragraphs
        if len(para) > 100:  # Skip short fragments
            md += f"{para}\n\n"
    
    # Add code blocks if any
    if code_blocks:
        md += "## Code Examples\n\n"
        for i, code in enumerate(code_blocks[:5], 1):
            md += f"### Example {i}\n\n"
            md += f"```\n{code[:1000]}\n```\n\n"  # Limit code length
    
    return md


def main():
    parser = argparse.ArgumentParser(description='Fetch and summarize web documentation')
    parser.add_argument('url', help='URL to fetch')
    parser.add_argument('--summary', '-s', action='store_true',
                       help='Output summary only')
    parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    parser.add_argument('--max-length', '-m', type=int, default=5000,
                       help='Maximum content length (default: 5000)')
    
    args = parser.parse_args()
    
    print(f"Fetching: {args.url}")
    
    html_content = fetch_url(args.url)
    if not html_content:
        sys.exit(1)
    
    title, text = extract_text(html_content)
    
    if args.summary:
        output = f"# {title}\n\n"
        output += summarize_text(text)
    else:
        code_blocks = extract_code_blocks(html_content)
        output = format_as_markdown(title, text[:args.max_length], args.url, code_blocks)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Saved to: {args.output}")
    else:
        print()
        print(output)


if __name__ == '__main__':
    main()
