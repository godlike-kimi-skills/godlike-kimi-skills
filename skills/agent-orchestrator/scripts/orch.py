#!/usr/bin/env python3
"""
Agent orchestrator for managing multi-agent systems.
Usage: orch.py <command> [options]
"""

import os
import sys
import json
import time
import psutil
import argparse
from datetime import datetime
from pathlib import Path
from collections import deque

ORCH_DIR = Path("D:/kimi/memory/agent-orchestrator")
ORCH_DIR.mkdir(parents=True, exist_ok=True)

POOLS_FILE = ORCH_DIR / "pools.json"
AGENTS_FILE = ORCH_DIR / "agents.json"
TASKS_FILE = ORCH_DIR / "tasks.json"

# Strategy functions
def strategy_round_robin(agents, task):
    """Round-robin selection."""
    ready = [a for a in agents if a['status'] == 'ready']
    if not ready:
        return None
    # Simple round-robin based on task count
    ready.sort(key=lambda a: a.get('task_count', 0))
    return ready[0]

def strategy_least_loaded(agents, task):
    """Select least loaded agent."""
    ready = [a for a in agents if a['status'] == 'ready']
    if not ready:
        return None
    ready.sort(key=lambda a: a.get('load', 0))
    return ready[0]

def strategy_priority(agents, task):
    """Priority-based selection (high priority agents first)."""
    ready = [a for a in agents if a['status'] == 'ready']
    if not ready:
        return None
    # Could be enhanced with agent priority levels
    return ready[0]

STRATEGIES = {
    'round-robin': strategy_round_robin,
    'least-loaded': strategy_least_loaded,
    'priority': strategy_priority
}


def load_pools():
    """Load agent pools."""
    if POOLS_FILE.exists():
        try:
            return json.loads(POOLS_FILE.read_text())
        except:
            return {}
    return {}


def save_pools(pools):
    """Save agent pools."""
    POOLS_FILE.write_text(json.dumps(pools, indent=2))


def load_agents():
    """Load agent definitions."""
    if AGENTS_FILE.exists():
        try:
            return json.loads(AGENTS_FILE.read_text())
        except:
            return []
    return []


def save_agents(agents):
    """Save agent definitions."""
    AGENTS_FILE.write_text(json.dumps(agents, indent=2))


def get_system_resources():
    """Get current system resource usage."""
    cpu_percent = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory()
    cpu_count = psutil.cpu_count()
    
    return {
        'cpu_percent': cpu_percent,
        'memory_percent': memory.percent,
        'cpu_count': cpu_count,
        'max_agents': cpu_count  # 1 per core rule
    }


def can_create_agent():
    """Check if we can create a new agent based on resources."""
    resources = get_system_resources()
    
    if resources['memory_percent'] > 80:
        return False, f"Memory too high: {resources['memory_percent']:.1f}%"
    
    agents = load_agents()
    active = len([a for a in agents if a['status'] != 'stopped'])
    
    if active >= resources['max_agents']:
        return False, f"Max agents reached: {active}/{resources['max_agents']}"
    
    return True, "OK"


def create_pool(name, size, strategy='round-robin', min_size=1, max_size=16):
    """Create a new agent pool."""
    pools = load_pools()
    
    if name in pools:
        print(f"[X] Pool '{name}' already exists")
        return
    
    # Validate size
    resources = get_system_resources()
    if size > resources['max_agents']:
        print(f"[!] Warning: Requested size {size} exceeds max agents {resources['max_agents']}")
        size = resources['max_agents']
    
    pool = {
        'name': name,
        'size': size,
        'strategy': strategy,
        'min_size': min_size,
        'max_size': max(max_size, size),
        'agents': [],
        'queue': [],
        'created': datetime.now().isoformat(),
        'updated': datetime.now().isoformat()
    }
    
    # Create initial agents
    for i in range(size):
        agent_id = f"{name}-{i+1}"
        agent = {
            'id': agent_id,
            'pool': name,
            'status': 'ready',
            'load': 0,
            'task_count': 0,
            'created': datetime.now().isoformat()
        }
        pool['agents'].append(agent_id)
        
        # Save to global agents list
        agents = load_agents()
        agents.append(agent)
        save_agents(agents)
    
    pools[name] = pool
    save_pools(pools)
    
    print(f"[OK] Created pool: {name}")
    print(f"   Size: {size}")
    print(f"   Strategy: {strategy}")
    print(f"   Agents: {', '.join(pool['agents'])}")


def list_pools():
    """List all pools."""
    pools = load_pools()
    agents = {a['id']: a for a in load_agents()}
    
    if not pools:
        print("\n[INFO] No pools created yet.\n")
        return
    
    print("\n[Agent Pools]\n")
    print(f"{'Name':<20} {'Size':<8} {'Strategy':<15} {'Queue':<8} {'Status'}")
    print("-" * 70)
    
    for name, pool in pools.items():
        # Count active agents
        active = sum(1 for aid in pool['agents'] if agents.get(aid, {}).get('status') == 'ready')
        queue_len = len(pool.get('queue', []))
        status = f"{active}/{pool['size']} ready"
        
        print(f"{name:<20} {pool['size']:<8} {pool['strategy']:<15} {queue_len:<8} {status}")
    
    print()


def scale_pool(name, new_size):
    """Scale pool to new size."""
    pools = load_pools()
    
    if name not in pools:
        print(f"[X] Pool '{name}' not found")
        return
    
    pool = pools[name]
    current_size = pool['size']
    
    # Check limits
    if new_size < pool['min_size']:
        print(f"[X] Cannot scale below minimum: {pool['min_size']}")
        return
    
    resources = get_system_resources()
    if new_size > min(pool['max_size'], resources['max_agents']):
        max_allowed = min(pool['max_size'], resources['max_agents'])
        print(f"[!] Scaling to maximum allowed: {max_allowed}")
        new_size = max_allowed
    
    agents = load_agents()
    
    if new_size > current_size:
        # Scale up - add agents
        for i in range(current_size, new_size):
            agent_id = f"{name}-{i+1}"
            agent = {
                'id': agent_id,
                'pool': name,
                'status': 'ready',
                'load': 0,
                'task_count': 0,
                'created': datetime.now().isoformat()
            }
            pool['agents'].append(agent_id)
            agents.append(agent)
        
        print(f"[OK] Scaled up: {current_size} → {new_size}")
        
    elif new_size < current_size:
        # Scale down - remove agents (prefer idle ones)
        to_remove = pool['agents'][new_size:]
        pool['agents'] = pool['agents'][:new_size]
        
        # Mark agents as stopped
        for agent_id in to_remove:
            for a in agents:
                if a['id'] == agent_id:
                    a['status'] = 'stopped'
        
        print(f"[OK] Scaled down: {current_size} → {new_size}")
    else:
        print(f"[INFO] No change needed")
        return
    
    pool['size'] = new_size
    pool['updated'] = datetime.now().isoformat()
    
    save_pools(pools)
    save_agents(agents)


def delete_pool(name):
    """Delete a pool."""
    pools = load_pools()
    
    if name not in pools:
        print(f"[X] Pool '{name}' not found")
        return
    
    pool = pools[name]
    
    # Stop all agents
    agents = load_agents()
    for agent_id in pool['agents']:
        for a in agents:
            if a['id'] == agent_id:
                a['status'] = 'stopped'
    
    del pools[name]
    
    save_pools(pools)
    save_agents(agents)
    
    print(f"[OK] Deleted pool: {name}")


def submit_task(pool_name, task_type, task_data=None, strategy=None, priority='normal'):
    """Submit a task to a pool."""
    pools = load_pools()
    agents = {a['id']: a for a in load_agents()}
    
    if pool_name not in pools:
        print(f"[X] Pool '{pool_name}' not found")
        return
    
    pool = pools[pool_name]
    use_strategy = strategy or pool['strategy']
    
    # Get pool agents
    pool_agents = [agents[aid] for aid in pool['agents'] if aid in agents]
    ready_agents = [a for a in pool_agents if a['status'] == 'ready']
    
    if not ready_agents:
        # Queue the task
        task = {
            'type': task_type,
            'data': task_data,
            'priority': priority,
            'submitted': datetime.now().isoformat(),
            'status': 'queued'
        }
        pool['queue'].append(task)
        save_pools(pools)
        print(f"[!] No ready agents. Task queued (#{len(pool['queue'])})")
        return
    
    # Select agent using strategy
    strategy_fn = STRATEGIES.get(use_strategy, strategy_round_robin)
    selected = strategy_fn(ready_agents, {'type': task_type, 'priority': priority})
    
    if not selected:
        print(f"[X] Could not select agent")
        return
    
    # Assign task
    task = {
        'type': task_type,
        'data': task_data,
        'agent': selected['id'],
        'priority': priority,
        'submitted': datetime.now().isoformat(),
        'status': 'assigned'
    }
    
    selected['load'] = selected.get('load', 0) + 1
    selected['task_count'] = selected.get('task_count', 0) + 1
    
    # Save updated agents
    all_agents = load_agents()
    for a in all_agents:
        if a['id'] == selected['id']:
            a['load'] = selected['load']
            a['task_count'] = selected['task_count']
    save_agents(all_agents)
    
    print(f"[OK] Task assigned to {selected['id']}")
    print(f"   Type: {task_type}")
    print(f"   Strategy: {use_strategy}")
    print(f"   Agent load: {selected['load']}")


def show_pool_status(name):
    """Show detailed pool status."""
    pools = load_pools()
    agents = {a['id']: a for a in load_agents()}
    
    if name not in pools:
        print(f"[X] Pool '{name}' not found")
        return
    
    pool = pools[name]
    
    print(f"\n[Pool: {name}]\n")
    print(f"Size: {pool['size']} (min: {pool['min_size']}, max: {pool['max_size']})")
    print(f"Strategy: {pool['strategy']}")
    print(f"Queue depth: {len(pool.get('queue', []))}")
    print(f"Created: {pool['created'][:19]}")
    print(f"\n[Agents]")
    
    for agent_id in pool['agents']:
        agent = agents.get(agent_id, {})
        status = agent.get('status', 'unknown')
        load = agent.get('load', 0)
        tasks = agent.get('task_count', 0)
        print(f"  {agent_id}: {status} (load: {load}, tasks: {tasks})")
    
    if pool.get('queue'):
        print(f"\n[Queue ({len(pool['queue'])} tasks)]")
        for i, task in enumerate(pool['queue'][:5], 1):
            print(f"  {i}. {task['type']} [{task['priority']}]")
        if len(pool['queue']) > 5:
            print(f"  ... and {len(pool['queue']) - 5} more")
    
    print()


def list_agents():
    """List all agents."""
    agents = load_agents()
    
    if not agents:
        print("\n[INFO] No agents created yet.\n")
        return
    
    print("\n[All Agents]\n")
    print(f"{'ID':<25} {'Pool':<15} {'Status':<10} {'Load':<8} {'Tasks'}")
    print("-" * 70)
    
    for agent in sorted(agents, key=lambda a: a['id']):
        print(f"{agent['id']:<25} {agent.get('pool', '-'):<15} "
              f"{agent['status']:<10} {agent.get('load', 0):<8} {agent.get('task_count', 0)}")
    
    print()


def health_check():
    """Run health checks on all agents."""
    agents = load_agents()
    pools = load_pools()
    
    if not agents:
        print("\n[INFO] No agents to check.\n")
        return
    
    print("\n[Health Check]\n")
    
    healthy = 0
    unhealthy = 0
    
    for agent in agents:
        if agent['status'] == 'stopped':
            continue
        
        # Simulate health check
        # In real implementation, would check process, memory, responsiveness
        agent_resources = get_system_resources()
        
        if agent_resources['memory_percent'] > 90:
            agent['status'] = 'unhealthy'
            agent['health_reason'] = 'high_memory'
            unhealthy += 1
            print(f"[X] {agent['id']}: UNHEALTHY (high memory)")
        elif agent.get('load', 0) > 10:
            agent['status'] = 'overloaded'
            unhealthy += 1
            print(f"[!] {agent['id']}: OVERLOADED (load: {agent['load']})")
        else:
            agent['status'] = 'ready'
            healthy += 1
            print(f"[OK] {agent['id']}: HEALTHY")
    
    save_agents(agents)
    
    print(f"\nSummary: {healthy} healthy, {unhealthy} unhealthy\n")


def auto_scale_dry_run():
    """Show what auto-scaling would do (dry run)."""
    pools = load_pools()
    resources = get_system_resources()
    
    print("\n[Auto-Scale Analysis]\n")
    print(f"System: {resources['cpu_count']} cores, {resources['memory_percent']:.1f}% memory")
    print(f"Max agents: {resources['max_agents']}")
    print()
    
    for name, pool in pools.items():
        queue_depth = len(pool.get('queue', []))
        per_agent = queue_depth / pool['size'] if pool['size'] > 0 else 0
        
        print(f"Pool: {name}")
        print(f"  Current: {pool['size']} agents")
        print(f"  Queue: {queue_depth} tasks ({per_agent:.1f} per agent)")
        
        if per_agent > 10 and resources['memory_percent'] < 70:
            recommended = min(pool['size'] + 2, pool['max_size'], resources['max_agents'])
            if recommended > pool['size']:
                print(f"  [SCALE UP] Recommended: {recommended}")
        elif per_agent < 2 and pool['size'] > pool['min_size']:
            recommended = max(pool['size'] - 1, pool['min_size'])
            print(f"  [SCALE DOWN] Recommended: {recommended}")
        else:
            print(f"  [NO CHANGE]")
        print()


def main():
    parser = argparse.ArgumentParser(description='Agent orchestrator')
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # Pool commands
    create_parser = subparsers.add_parser('pool-create', help='Create agent pool')
    create_parser.add_argument('--name', required=True, help='Pool name')
    create_parser.add_argument('--size', type=int, default=3, help='Initial size')
    create_parser.add_argument('--strategy', default='round-robin',
                              choices=list(STRATEGIES.keys()),
                              help='Load balancing strategy')
    create_parser.add_argument('--min', type=int, default=1, help='Minimum size')
    create_parser.add_argument('--max', type=int, default=16, help='Maximum size')
    
    subparsers.add_parser('pools', help='List all pools')
    
    scale_parser = subparsers.add_parser('pool-scale', help='Scale pool')
    scale_parser.add_argument('--name', required=True, help='Pool name')
    scale_parser.add_argument('--size', type=int, required=True, help='New size')
    
    delete_parser = subparsers.add_parser('pool-delete', help='Delete pool')
    delete_parser.add_argument('--name', required=True, help='Pool name')
    
    # Task commands
    submit_parser = subparsers.add_parser('submit', help='Submit task')
    submit_parser.add_argument('--pool', required=True, help='Pool name')
    submit_parser.add_argument('--task', required=True, help='Task type')
    submit_parser.add_argument('--data', help='Task data')
    submit_parser.add_argument('--strategy', choices=list(STRATEGIES.keys()),
                              help='Override pool strategy')
    submit_parser.add_argument('--priority', default='normal',
                              choices=['critical', 'high', 'normal', 'low'])
    
    # Status commands
    status_parser = subparsers.add_parser('status', help='Show pool status')
    status_parser.add_argument('--pool', help='Pool name (omit for all)')
    
    subparsers.add_parser('agents', help='List all agents')
    subparsers.add_parser('health', help='Run health checks')
    subparsers.add_parser('auto-scale-dry-run', help='Show auto-scale recommendations')
    
    args = parser.parse_args()
    
    if args.command == 'pool-create':
        create_pool(args.name, args.size, args.strategy, args.min, args.max)
    elif args.command == 'pools':
        list_pools()
    elif args.command == 'pool-scale':
        scale_pool(args.name, args.size)
    elif args.command == 'pool-delete':
        delete_pool(args.name)
    elif args.command == 'submit':
        submit_task(args.pool, args.task, args.data, args.strategy, args.priority)
    elif args.command == 'status':
        if args.pool:
            show_pool_status(args.pool)
        else:
            list_pools()
    elif args.command == 'agents':
        list_agents()
    elif args.command == 'health':
        health_check()
    elif args.command == 'auto-scale-dry-run':
        auto_scale_dry_run()
    else:
        list_pools()


if __name__ == '__main__':
    main()
