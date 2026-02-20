#!/usr/bin/env python3
"""
Code search for development research.
Usage: search.py <query> [--site <site>] [--save <file>]
"""

import sys
import webbrowser
import urllib.parse
import argparse


def search_stackoverflow(query):
    """Search Stack Overflow."""
    url = f"https://stackoverflow.com/search?q={urllib.parse.quote(query)}"
    return url


def search_github(query):
    """Search GitHub."""
    url = f"https://github.com/search?q={urllib.parse.quote(query)}&type=code"
    return url


def search_google(query):
    """Search Google with programming focus."""
    url = f"https://www.google.com/search?q={urllib.parse.quote(query + ' programming')}"
    return url


def search_docs(query):
    """Search documentation sites."""
    # Try to guess documentation URL based on keywords
    keywords = query.lower().split()
    
    doc_urls = {
        'python': 'https://docs.python.org/3/search.html?q=',
        'django': 'https://docs.djangoproject.com/search/?q=',
        'flask': 'https://flask.palletsprojects.com/search?q=',
        'fastapi': 'https://fastapi.tiangolo.com/search/?q=',
        'react': 'https://react.dev/search?q=',
        'vue': 'https://vuejs.org/search/?q=',
        'angular': 'https://angular.io/search?q=',
        'nodejs': 'https://nodejs.org/docs/search?q=',
        'docker': 'https://docs.docker.com/search/?q=',
        'kubernetes': 'https://kubernetes.io/search/?q=',
        'aws': 'https://docs.aws.amazon.com/search/doc-search.html?searchQuery=',
        'azure': 'https://docs.microsoft.com/en-us/search/?terms=',
    }
    
    for keyword, base_url in doc_urls.items():
        if keyword in keywords:
            return base_url + urllib.parse.quote(query)
    
    # Default to Google
    return search_google(query + " documentation")


def search_npm(query):
    """Search npm packages."""
    url = f"https://www.npmjs.com/search?q={urllib.parse.quote(query)}"
    return url


def search_pypi(query):
    """Search PyPI packages."""
    url = f"https://pypi.org/search/?q={urllib.parse.quote(query)}"
    return url


def format_results(query, site):
    """Format search results info."""
    results = []
    
    results.append(f"# Code Search Results\n")
    results.append(f"**Query:** {query}\n")
    results.append(f"**Source:** {site or 'Multiple'}\n")
    results.append("---\n")
    
    results.append("## Search Links\n")
    
    if site == 'stackoverflow' or not site:
        results.append(f"### Stack Overflow")
        results.append(f"{search_stackoverflow(query)}\n")
        results.append(f"- Best for: Q&A, error solutions, how-to guides\n")
    
    if site == 'github' or not site:
        results.append(f"### GitHub")
        results.append(f"{search_github(query)}\n")
        results.append(f"- Best for: Real code examples, project references\n")
    
    if site == 'docs' or not site:
        results.append(f"### Documentation")
        results.append(f"{search_docs(query)}\n")
        results.append(f"- Best for: Official docs, API references\n")
    
    if not site:
        results.append(f"### Google")
        results.append(f"{search_google(query)}\n")
        results.append(f"- Best for: Broad search, tutorials, articles\n")
    
    results.append("\n## Search Tips\n")
    results.append("- Use specific keywords (language, framework, version)")
    results.append("- Add 'example' or 'tutorial' for learning resources")
    results.append("- Add 'best practice' for patterns and guidelines")
    results.append("- Check multiple sources for comprehensive answers")
    
    return '\n'.join(results)


def main():
    parser = argparse.ArgumentParser(description='Code search for developers')
    parser.add_argument('query', help='Search query')
    parser.add_argument('--site', '-s', 
                       choices=['stackoverflow', 'github', 'docs', 'npm', 'pypi'],
                       help='Specific site to search')
    parser.add_argument('--open', '-o', action='store_true',
                       help='Open in browser')
    parser.add_argument('--save', '-f', help='Save results to file')
    
    args = parser.parse_args()
    
    print(f"🔍 Searching: {args.query}")
    if args.site:
        print(f"   Source: {args.site}")
    print()
    
    # Generate search URLs
    urls = {}
    
    if args.site == 'stackoverflow':
        urls['Stack Overflow'] = search_stackoverflow(args.query)
    elif args.site == 'github':
        urls['GitHub'] = search_github(args.query)
    elif args.site == 'docs':
        urls['Documentation'] = search_docs(args.query)
    elif args.site == 'npm':
        urls['npm'] = search_npm(args.query)
    elif args.site == 'pypi':
        urls['PyPI'] = search_pypi(args.query)
    else:
        urls['Stack Overflow'] = search_stackoverflow(args.query)
        urls['GitHub'] = search_github(args.query)
        urls['Documentation'] = search_docs(args.query)
        urls['Google'] = search_google(args.query)
    
    # Display results
    print("Search Links:")
    print()
    for name, url in urls.items():
        print(f"  {name}:")
        print(f"    {url}")
        print()
    
    # Open in browser if requested
    if args.open:
        for url in urls.values():
            webbrowser.open(url)
        print("🌐 Opening in browser...")
    
    # Save to file if requested
    if args.save:
        content = format_results(args.query, args.site)
        with open(args.save, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"💾 Saved to: {args.save}")


if __name__ == '__main__':
    main()
