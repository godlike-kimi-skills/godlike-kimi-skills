#!/usr/bin/env python3
"""Brave Search - Privacy-focused search"""

import argparse
import json
from datetime import datetime, timedelta
from typing import Dict, List


def web_search(query: str, limit: int = 10) -> Dict:
    """Perform web search"""
    # Simulated search results
    results = []
    for i in range(min(limit, 10)):
        results.append({
            'title': f'Result {i+1} for "{query}"',
            'url': f'https://example.com/result{i+1}',
            'description': f'This is a sample search result description for query: {query}',
            'source': 'Brave Search'
        })
    
    return {
        'query': query,
        'results_count': len(results),
        'results': results,
        'searched_at': datetime.now().isoformat()
    }


def image_search(query: str, output: str = None) -> Dict:
    """Search for images"""
    results = [
        {'url': f'https://example.com/image{i}.jpg', 'title': f'Image {i}'} 
        for i in range(1, 6)
    ]
    
    result = {
        'query': query,
        'images': results,
        'searched_at': datetime.now().isoformat()
    }
    
    if output:
        with open(output, 'w') as f:
            json.dump(result, f, indent=2)
    
    return result


def news_search(query: str, days: int = 7) -> Dict:
    """Search for news"""
    since = datetime.now() - timedelta(days=days)
    
    articles = [
        {
            'title': f'News about {query}',
            'source': 'News Source',
            'published': (since + timedelta(days=i)).isoformat(),
            'url': f'https://news.example.com/article{i}'
        }
        for i in range(5)
    ]
    
    return {
        'query': query,
        'since': since.strftime('%Y-%m-%d'),
        'articles': articles,
        'searched_at': datetime.now().isoformat()
    }


def main():
    parser = argparse.ArgumentParser(description='Brave Search')
    subparsers = parser.add_subparsers(dest='command')
    
    web_parser = subparsers.add_parser('query')
    web_parser.add_argument('search_query')
    web_parser.add_argument('--limit', type=int, default=10)
    
    image_parser = subparsers.add_parser('images')
    image_parser.add_argument('search_query')
    image_parser.add_argument('--output')
    
    news_parser = subparsers.add_parser('news')
    news_parser.add_argument('search_query')
    news_parser.add_argument('--days', type=int, default=7)
    
    args = parser.parse_args()
    
    if args.command == 'query':
        result = web_search(args.search_query, args.limit)
        print(json.dumps(result, indent=2))
    elif args.command == 'images':
        result = image_search(args.search_query, args.output)
        print(json.dumps(result, indent=2))
    elif args.command == 'news':
        result = news_search(args.search_query, args.days)
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
