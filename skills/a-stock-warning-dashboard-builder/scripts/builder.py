#!/usr/bin/env python3
"""A-Stock Warning Dashboard Builder"""

import argparse
import json
from datetime import datetime
from pathlib import Path


DASHBOARDS_DIR = Path.home() / '.kimi' / 'dashboards'


def create_dashboard(name: str):
    """Create new dashboard"""
    DASHBOARDS_DIR.mkdir(parents=True, exist_ok=True)
    
    dashboard = {
        'name': name,
        'created_at': datetime.now().isoformat(),
        'widgets': [],
        'rules': []
    }
    
    file_path = DASHBOARDS_DIR / f"{name}.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(dashboard, f, indent=2)
    
    print(f"Created dashboard: {name}")
    return dashboard


def add_rule(dashboard_name: str, ts_code: str, condition: str):
    """Add warning rule to dashboard"""
    file_path = DASHBOARDS_DIR / f"{dashboard_name}.json"
    
    if not file_path.exists():
        print(f"Dashboard not found: {dashboard_name}")
        return
    
    with open(file_path, 'r') as f:
        dashboard = json.load(f)
    
    rule = {
        'id': len(dashboard['rules']) + 1,
        'ts_code': ts_code,
        'condition': condition,
        'status': 'active',
        'created_at': datetime.now().isoformat()
    }
    
    dashboard['rules'].append(rule)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(dashboard, f, indent=2)
    
    print(f"Added rule to {dashboard_name}: {ts_code} - {condition}")


def monitor_dashboard(name: str):
    """Start monitoring dashboard"""
    file_path = DASHBOARDS_DIR / f"{name}.json"
    
    if not file_path.exists():
        print(f"Dashboard not found: {name}")
        return
    
    with open(file_path, 'r') as f:
        dashboard = json.load(f)
    
    print(f"Monitoring dashboard: {name}")
    print(f"Active rules: {len(dashboard['rules'])}")
    print("\nSimulated monitoring (press Ctrl+C to stop):")
    
    for rule in dashboard['rules']:
        print(f"  [{datetime.now().strftime('%H:%M:%S')}] Checking {rule['ts_code']}: OK")


def list_dashboards():
    """List all dashboards"""
    if not DASHBOARDS_DIR.exists():
        print("No dashboards found")
        return
    
    dashboards = list(DASHBOARDS_DIR.glob('*.json'))
    print(f"Found {len(dashboards)} dashboards:")
    for db_file in dashboards:
        with open(db_file, 'r') as f:
            data = json.load(f)
            print(f"  - {data['name']} ({len(data['rules'])} rules)")


def main():
    parser = argparse.ArgumentParser(description='A-Stock Warning Dashboard Builder')
    subparsers = parser.add_subparsers(dest='command')
    
    create_parser = subparsers.add_parser('create')
    create_parser.add_argument('--name', required=True)
    
    rule_parser = subparsers.add_parser('rule')
    rule_parser.add_argument('action', choices=['add'])
    rule_parser.add_argument('--dashboard', required=True)
    rule_parser.add_argument('--code', required=True)
    rule_parser.add_argument('--condition', required=True)
    
    monitor_parser = subparsers.add_parser('monitor')
    monitor_parser.add_argument('--dashboard', required=True)
    
    subparsers.add_parser('list')
    
    args = parser.parse_args()
    
    if args.command == 'create':
        create_dashboard(args.name)
    elif args.command == 'rule' and args.action == 'add':
        add_rule(args.dashboard, args.code, args.condition)
    elif args.command == 'monitor':
        monitor_dashboard(args.dashboard)
    elif args.command == 'list':
        list_dashboards()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
