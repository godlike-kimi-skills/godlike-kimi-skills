#!/usr/bin/env python3
"""File Organizer - Smart file organization tool"""

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List


FILE_TYPES = {
    'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'],
    'Documents': ['.pdf', '.doc', '.docx', '.txt', '.md', '.xls', '.xlsx', '.ppt', '.pptx'],
    'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv'],
    'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
    'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
    'Code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', '.go', '.rs']
}


def get_file_category(file_path: Path) -> str:
    """Determine file category by extension"""
    ext = file_path.suffix.lower()
    for category, extensions in FILE_TYPES.items():
        if ext in extensions:
            return category
    return 'Others'


def organize_by_type(source_dir: str, target_dir: str = None, dry_run: bool = False):
    """Organize files by type"""
    source = Path(source_dir)
    target = Path(target_dir) if target_dir else source
    
    if not source.exists():
        print(f"Source directory not found: {source_dir}")
        return
    
    operations = []
    for file_path in source.iterdir():
        if file_path.is_file():
            category = get_file_category(file_path)
            dest_dir = target / category
            dest_path = dest_dir / file_path.name
            
            operations.append({
                'source': str(file_path),
                'destination': str(dest_path),
                'category': category
            })
            
            if not dry_run:
                dest_dir.mkdir(exist_ok=True)
                shutil.move(str(file_path), str(dest_path))
    
    print(f"{'Would move' if dry_run else 'Moved'} {len(operations)} files")
    return operations


def organize_by_date(source_dir: str, target_dir: str, move: bool = False):
    """Organize files by date"""
    source = Path(source_dir)
    target = Path(target_dir)
    
    for file_path in source.iterdir():
        if file_path.is_file():
            stat = file_path.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime)
            date_dir = target / f"{mtime.year}" / f"{mtime.month:02d}"
            date_dir.mkdir(parents=True, exist_ok=True)
            
            dest = date_dir / file_path.name
            if move:
                shutil.move(str(file_path), str(dest))
            else:
                shutil.copy2(str(file_path), str(dest))
    
    print(f"Organized files by date to: {target}")


def add_rule(pattern: str, action: str, target: str):
    """Add organization rule"""
    rule = {
        'pattern': pattern,
        'action': action,
        'target': target,
        'created_at': datetime.now().isoformat()
    }
    print(f"Added rule: {json.dumps(rule, indent=2)}")


def main():
    parser = argparse.ArgumentParser(description='File Organizer')
    subparsers = parser.add_subparsers(dest='command')
    
    org_parser = subparsers.add_parser('organize')
    org_parser.add_argument('source')
    org_parser.add_argument('--by-type', action='store_true')
    org_parser.add_argument('--by-date', action='store_true')
    org_parser.add_argument('--target')
    org_parser.add_argument('--move', action='store_true')
    org_parser.add_argument('--dry-run', action='store_true')
    
    rule_parser = subparsers.add_parser('rule')
    rule_parser.add_argument('action', choices=['add', 'list'])
    rule_parser.add_argument('--pattern')
    rule_parser.add_argument('--target')
    
    args = parser.parse_args()
    
    if args.command == 'organize':
        if args.by_type:
            organize_by_type(args.source, args.target, args.dry_run)
        elif args.by_date:
            organize_by_date(args.source, args.target or args.source, args.move)
    elif args.command == 'rule' and args.action == 'add':
        add_rule(args.pattern, 'move', args.target)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
