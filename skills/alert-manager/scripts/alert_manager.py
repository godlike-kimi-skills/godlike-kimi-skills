#!/usr/bin/env python3
"""Alert Manager - Alert management system"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List


ALERTS_DIR = Path.home() / '.kimi' / 'alerts'
ALERTS_FILE = ALERTS_DIR / 'alerts.json'


def load_alerts() -> List[Dict]:
    """Load alerts from file"""
    if ALERTS_FILE.exists():
        with open(ALERTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_alerts(alerts: List[Dict]):
    """Save alerts to file"""
    ALERTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(ALERTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(alerts, f, indent=2)


def create_rule(name: str, condition: str, severity: str = 'warning'):
    """Create alert rule"""
    alerts = load_alerts()
    rule = {
        'id': len(alerts) + 1,
        'name': name,
        'condition': condition,
        'severity': severity,
        'status': 'active',
        'created_at': datetime.now().isoformat()
    }
    alerts.append(rule)
    save_alerts(alerts)
    print(f"Created alert rule: {name}")


def list_alerts(status: str = None):
    """List all alerts"""
    alerts = load_alerts()
    
    if status:
        alerts = [a for a in alerts if a.get('status') == status]
    
    print(json.dumps(alerts, indent=2))


def add_notification(channel: str, target: str):
    """Add notification channel"""
    config = {
        'channel': channel,
        'target': target,
        'configured_at': datetime.now().isoformat()
    }
    print(f"Added notification: {json.dumps(config, indent=2)}")


def simulate_alert(rule_name: str):
    """Simulate alert firing"""
    print(f"ALERT: {rule_name}")
    print(f"Severity: warning")
    print(f"Time: {datetime.now().isoformat()}")
    print("Message: Threshold exceeded")


def main():
    parser = argparse.ArgumentParser(description='Alert Manager')
    subparsers = parser.add_subparsers(dest='command')
    
    rule_parser = subparsers.add_parser('rule')
    rule_parser.add_argument('action', choices=['create', 'list'])
    rule_parser.add_argument('--name')
    rule_parser.add_argument('--condition')
    rule_parser.add_argument('--severity', default='warning')
    
    notify_parser = subparsers.add_parser('notify')
    notify_parser.add_argument('action', choices=['add'])
    notify_parser.add_argument('--channel', required=True)
    notify_parser.add_argument('--target', required=True)
    
    list_parser = subparsers.add_parser('list')
    list_parser.add_argument('--status')
    
    simulate_parser = subparsers.add_parser('simulate')
    simulate_parser.add_argument('--rule', required=True)
    
    args = parser.parse_args()
    
    if args.command == 'rule' and args.action == 'create':
        create_rule(args.name, args.condition, args.severity)
    elif args.command == 'list':
        list_alerts(args.status)
    elif args.command == 'notify' and args.action == 'add':
        add_notification(args.channel, args.target)
    elif args.command == 'simulate':
        simulate_alert(args.rule)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
