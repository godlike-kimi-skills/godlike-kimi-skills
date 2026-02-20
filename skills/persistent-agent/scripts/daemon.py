#!/usr/bin/env python3
"""
Persistent Agent Daemon Manager
Based on systemd and supervisord patterns
"""

import argparse
import json
import signal
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class AgentProcess:
    """Represents a managed agent process"""

    def __init__(self, name: str, command: str, auto_start: bool = True):
        self.name = name
        self.command = command
        self.auto_start = auto_start
        self.process: Optional[subprocess.Popen] = None
        self.start_time: Optional[datetime] = None
        self.restart_count = 0
        self.status = 'stopped'

    def start(self) -> bool:
        """Start the process"""
        try:
            self.process = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.start_time = datetime.now()
            self.status = 'running'
            return True
        except Exception as e:
            self.status = f'error: {e}'
            return False

    def stop(self) -> bool:
        """Stop the process"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                self.status = 'stopped'
                return True
            except:
                self.process.kill()
                return False
        return True

    def is_running(self) -> bool:
        """Check if process is running"""
        return self.process is not None and self.process.poll() is None

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'command': self.command,
            'status': self.status,
            'pid': self.process.pid if self.is_running() else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'restart_count': self.restart_count
        }


class DaemonManager:
    """Manages persistent agents"""

    CONFIG_FILE = Path.home() / '.persistent_agents.json'

    def __init__(self):
        self.agents: Dict[str, AgentProcess] = {}
        self.load_config()

    def load_config(self):
        """Load agent configurations"""
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    for name, agent_config in config.items():
                        self.agents[name] = AgentProcess(
                            name=name,
                            command=agent_config.get('command', ''),
                            auto_start=agent_config.get('auto_start', True)
                        )
            except Exception:
                pass

    def save_config(self):
        """Save agent configurations"""
        config = {
            name: {
                'command': agent.command,
                'auto_start': agent.auto_start
            }
            for name, agent in self.agents.items()
        }
        with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)

    def register(self, name: str, command: str, auto_start: bool = True) -> bool:
        """Register a new agent"""
        self.agents[name] = AgentProcess(name, command, auto_start)
        self.save_config()
        return True

    def start(self, name: str) -> bool:
        """Start an agent"""
        if name not in self.agents:
            print(f'Agent not found: {name}')
            return False
        return self.agents[name].start()

    def stop(self, name: str) -> bool:
        """Stop an agent"""
        if name not in self.agents:
            print(f'Agent not found: {name}')
            return False
        return self.agents[name].stop()

    def status(self, name: Optional[str] = None) -> Dict:
        """Get agent status"""
        if name:
            if name in self.agents:
                return self.agents[name].to_dict()
            return {'error': f'Agent not found: {name}'}
        return {name: agent.to_dict() for name, agent in self.agents.items()}

    def list_agents(self) -> List[Dict]:
        """List all agents"""
        return [agent.to_dict() for agent in self.agents.values()]


def main():
    parser = argparse.ArgumentParser(description='Persistent Agent Daemon')
    subparsers = parser.add_subparsers(dest='command')

    register_parser = subparsers.add_parser('register')
    register_parser.add_argument('name')
    register_parser.add_argument('--cmd', required=True)
    register_parser.add_argument('--auto-start', action='store_true')

    subparsers.add_parser('start').add_argument('name')
    subparsers.add_parser('stop').add_argument('name')
    subparsers.add_parser('status').add_argument('name', nargs='?')
    subparsers.add_parser('list')

    args = parser.parse_args()
    manager = DaemonManager()

    if args.command == 'register':
        manager.register(args.name, args.cmd, args.auto_start)
        print(f'Registered agent: {args.name}')

    elif args.command == 'start':
        if manager.start(args.name):
            print(f'Started agent: {args.name}')
        else:
            print(f'Failed to start agent: {args.name}')
            sys.exit(1)

    elif args.command == 'stop':
        if manager.stop(args.name):
            print(f'Stopped agent: {args.name}')
        else:
            print(f'Failed to stop agent: {args.name}')
            sys.exit(1)

    elif args.command == 'status':
        status = manager.status(args.name)
        print(json.dumps(status, indent=2))

    elif args.command == 'list':
        agents = manager.list_agents()
        print(json.dumps(agents, indent=2))


if __name__ == '__main__':
    main()
