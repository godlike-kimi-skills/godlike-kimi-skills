#!/usr/bin/env python3
"""Log Manager - Log analysis and management tool"""

import argparse
import gzip
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List


def view_log(file_path: str, tail: int = None, head: int = None):
    """View log file"""
    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {file_path}")
        return
    
    # Handle gzipped files
    if file_path.endswith('.gz'):
        with gzip.open(file_path, 'rt', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    else:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    
    if head:
        lines = lines[:head]
    elif tail:
        lines = lines[-tail:]
    
    for line in lines:
        print(line.rstrip())


def search_logs(pattern: str, files: str, since: str = None):
    """Search logs for pattern"""
    import glob
    
    log_files = glob.glob(files)
    results = []
    
    since_time = None
    if since:
        if since.endswith('h'):
            hours = int(since[:-1])
            since_time = datetime.now() - timedelta(hours=hours)
    
    for log_file in log_files:
        path = Path(log_file)
        if not path.exists():
            continue
        
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    results.append({
                        'file': log_file,
                        'line': i,
                        'content': line.strip()[:200]
                    })
    
    print(json.dumps(results[:100], indent=2))
    print(f"\nFound {len(results)} matches")


def analyze_patterns(file_path: str, pattern: str):
    """Analyze log patterns"""
    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {file_path}")
        return
    
    counts = {}
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            matches = re.findall(pattern, line)
            for match in matches:
                counts[match] = counts.get(match, 0) + 1
    
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    print(json.dumps(dict(sorted_counts[:20]), indent=2))


def main():
    parser = argparse.ArgumentParser(description='Log Manager')
    subparsers = parser.add_subparsers(dest='command')
    
    view_parser = subparsers.add_parser('view')
    view_parser.add_argument('file')
    view_parser.add_argument('--tail', type=int)
    view_parser.add_argument('--head', type=int)
    
    search_parser = subparsers.add_parser('search')
    search_parser.add_argument('pattern')
    search_parser.add_argument('--files', required=True)
    search_parser.add_argument('--since')
    
    analyze_parser = subparsers.add_parser('analyze')
    analyze_parser.add_argument('--file', required=True)
    analyze_parser.add_argument('--pattern', required=True)
    
    args = parser.parse_args()
    
    if args.command == 'view':
        view_log(args.file, args.tail, args.head)
    elif args.command == 'search':
        search_logs(args.pattern, args.files, args.since)
    elif args.command == 'analyze':
        analyze_patterns(args.file, args.pattern)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
