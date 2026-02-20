#!/usr/bin/env python3
"""Workflow Builder - Build and run automation workflows"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List


WORKFLOW_DIR = Path.home() / '.kimi' / 'workflows'


class Workflow:
    def __init__(self, name: str):
        self.name = name
        self.steps = []
        self.trigger = None
        self.created_at = datetime.now().isoformat()
    
    def add_step(self, action: str, params: Dict):
        self.steps.append({'action': action, 'params': params})
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'trigger': self.trigger,
            'steps': self.steps,
            'created_at': self.created_at
        }
    
    def save(self):
        WORKFLOW_DIR.mkdir(parents=True, exist_ok=True)
        file_path = WORKFLOW_DIR / f"{self.name}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)


def create_workflow(name: str, template: str = 'empty'):
    """Create a new workflow"""
    wf = Workflow(name)
    
    if template == 'cron':
        wf.trigger = {'type': 'cron', 'schedule': '0 9 * * *'}
        wf.add_step('log', {'message': 'Daily report started'})
    elif template == 'file':
        wf.trigger = {'type': 'file', 'path': '~/Downloads'}
    
    wf.save()
    print(f"Created workflow: {name}")
    return wf


def list_workflows():
    """List all workflows"""
    if not WORKFLOW_DIR.exists():
        print("No workflows found")
        return
    
    workflows = list(WORKFLOW_DIR.glob('*.json'))
    print(f"Found {len(workflows)} workflows:")
    for wf_file in workflows:
        with open(wf_file, 'r') as f:
            data = json.load(f)
            print(f"  - {data['name']} ({len(data['steps'])} steps)")


def run_workflow(name: str):
    """Run a workflow"""
    wf_file = WORKFLOW_DIR / f"{name}.json"
    if not wf_file.exists():
        print(f"Workflow not found: {name}")
        return
    
    with open(wf_file, 'r') as f:
        data = json.load(f)
    
    print(f"Running workflow: {name}")
    for i, step in enumerate(data['steps'], 1):
        print(f"  Step {i}: {step['action']}")
    print("Workflow completed")


def main():
    parser = argparse.ArgumentParser(description='Workflow Builder')
    subparsers = parser.add_subparsers(dest='command')
    
    create_parser = subparsers.add_parser('create')
    create_parser.add_argument('--name', required=True)
    create_parser.add_argument('--template', default='empty')
    
    subparsers.add_parser('list')
    
    run_parser = subparsers.add_parser('run')
    run_parser.add_argument('name')
    
    args = parser.parse_args()
    
    if args.command == 'create':
        create_workflow(args.name, args.template)
    elif args.command == 'list':
        list_workflows()
    elif args.command == 'run':
        run_workflow(args.name)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
