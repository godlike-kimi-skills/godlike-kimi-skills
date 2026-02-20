#!/usr/bin/env python3
"""Dev Efficiency - Developer productivity tools"""

import argparse
import json
from datetime import datetime
from pathlib import Path


ALIASES = {
    'powershell': {
        'g': 'git',
        'gs': 'git status',
        'ga': 'git add',
        'gc': 'git commit -m',
        'gp': 'git push',
        'gco': 'git checkout',
        'k': 'kimi',
        'll': 'ls -la',
    },
    'bash': {
        'g': 'git',
        'gs': 'git status',
        'ga': 'git add',
        'gc': 'git commit -m',
        'gp': 'git push',
        'gco': 'git checkout',
        'k': 'kimi',
        'll': 'ls -la',
    }
}


TEMPLATES = {
    'python': {
        'dirs': ['src', 'tests', 'docs'],
        'files': {
            'README.md': '# Project Name\n\nDescription here.',
            'requirements.txt': '',
            'setup.py': 'from setuptools import setup\nsetup(name="project", version="0.1.0")'
        }
    },
    'node': {
        'dirs': ['src', 'test'],
        'files': {
            'README.md': '# Project Name\n\nDescription here.',
            'package.json': '{"name": "project", "version": "0.1.0"}'
        }
    }
}


def install_aliases(shell: str):
    """Install shell aliases"""
    aliases = ALIASES.get(shell, ALIASES['bash'])
    
    print(f"# Add these to your {shell} profile:")
    print()
    
    if shell == 'powershell':
        for alias, command in aliases.items():
            print(f"Set-Alias -Name {alias} -Value {command}")
    else:
        for alias, command in aliases.items():
            print(f"alias {alias}='{command}'")


def init_project(template: str, name: str):
    """Initialize project from template"""
    tmpl = TEMPLATES.get(template)
    if not tmpl:
        print(f"Unknown template: {template}")
        return
    
    project_dir = Path(name)
    project_dir.mkdir(exist_ok=True)
    
    for dir_name in tmpl['dirs']:
        (project_dir / dir_name).mkdir(exist_ok=True)
    
    for file_name, content in tmpl['files'].items():
        (project_dir / file_name).write_text(content, encoding='utf-8')
    
    print(f"Created {template} project: {name}")


def show_stats(days: int):
    """Show efficiency statistics"""
    stats = {
        'period': f'Last {days} days',
        'commands_executed': 0,
        'time_saved': '0h',
        'most_used': ['git status', 'kimi', 'ls'],
        'generated_at': datetime.now().isoformat()
    }
    print(json.dumps(stats, indent=2))


def main():
    parser = argparse.ArgumentParser(description='Dev Efficiency Tools')
    subparsers = parser.add_subparsers(dest='command')
    
    alias_parser = subparsers.add_parser('install-aliases')
    alias_parser.add_argument('--shell', choices=['powershell', 'bash'], required=True)
    
    init_parser = subparsers.add_parser('init')
    init_parser.add_argument('--template', choices=['python', 'node'], required=True)
    init_parser.add_argument('--name', required=True)
    
    stats_parser = subparsers.add_parser('stats')
    stats_parser.add_argument('--days', type=int, default=7)
    
    args = parser.parse_args()
    
    if args.command == 'install-aliases':
        install_aliases(args.shell)
    elif args.command == 'init':
        init_project(args.template, args.name)
    elif args.command == 'stats':
        show_stats(args.days)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
