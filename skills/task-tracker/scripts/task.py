#!/usr/bin/env python3
"""
Task tracker v2.0 with dependencies and workflow support.
Usage: task.py <command> [options]
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from collections import defaultdict

TASKS_DIR = Path("D:/kimi/memory/tasks")
TASKS_FILE = TASKS_DIR / "tasks.json"
WORKFLOWS_FILE = TASKS_DIR / "workflows.json"

PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
STATUS_ORDER = {"blocked": 0, "pending": 1, "in-progress": 2, "done": 3}

# Workflow templates
WORKFLOW_TEMPLATES = {
    "software-release": {
        "name": "Software Release",
        "tasks": [
            {"title": "Create release plan", "priority": "high", "tags": ["planning"]},
            {"title": "Finalize features", "priority": "high", "tags": ["dev"]},
            {"title": "QA testing", "priority": "critical", "tags": ["testing"]},
            {"title": "Production deployment", "priority": "critical", "tags": ["deploy"]}
        ]
    },
    "bug-fix": {
        "name": "Bug Fix",
        "tasks": [
            {"title": "Reproduce and analyze bug", "priority": "high", "tags": ["analysis"]},
            {"title": "Implement fix", "priority": "high", "tags": ["dev"]},
            {"title": "Verify fix", "priority": "critical", "tags": ["testing"]},
            {"title": "Close issue", "priority": "medium", "tags": ["cleanup"]}
        ]
    },
    "feature-dev": {
        "name": "Feature Development",
        "tasks": [
            {"title": "Design feature", "priority": "high", "tags": ["design"]},
            {"title": "Implement feature", "priority": "high", "tags": ["dev"]},
            {"title": "Code review", "priority": "medium", "tags": ["review"]},
            {"title": "Merge to main", "priority": "medium", "tags": ["merge"]}
        ]
    }
}


def ensure_storage():
    """Ensure task storage exists."""
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    if not TASKS_FILE.exists():
        save_tasks([])
    if not WORKFLOWS_FILE.exists():
        WORKFLOWS_FILE.write_text(json.dumps({}))


def load_tasks():
    """Load all tasks."""
    ensure_storage()
    try:
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []


def save_tasks(tasks):
    """Save all tasks."""
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)


def get_next_id(tasks):
    """Get next task ID."""
    if not tasks:
        return 1
    return max(t['id'] for t in tasks) + 1


def check_dependencies(tasks, task_id):
    """Check if task dependencies are satisfied."""
    task = next((t for t in tasks if t['id'] == task_id), None)
    if not task or not task.get('depends_on'):
        return True, []
    
    blocking = []
    for dep_id in task['depends_on']:
        dep = next((t for t in tasks if t['id'] == dep_id), None)
        if dep and dep['status'] != 'done':
            blocking.append(dep_id)
    
    return len(blocking) == 0, blocking


def update_blocked_status(tasks):
    """Update blocked status for all tasks."""
    for task in tasks:
        if task['status'] == 'done':
            continue
        
        can_run, blocking = check_dependencies(tasks, task['id'])
        if task.get('depends_on') and not can_run:
            task['status'] = 'blocked'
            task['blocked_by'] = blocking
        elif task['status'] == 'blocked' and can_run:
            task['status'] = 'pending'
            task.pop('blocked_by', None)
    
    return tasks


def add_task(title, priority="medium", description="", tags=None, depends_on=None, estimated_hours=None):
    """Add a new task."""
    tasks = load_tasks()
    
    # Parse dependencies
    deps = None
    if depends_on:
        deps = [int(d.strip()) for d in depends_on.split(',')]
    
    task = {
        "id": get_next_id(tasks),
        "title": title,
        "description": description,
        "priority": priority,
        "status": "blocked" if deps else "pending",
        "tags": tags or [],
        "depends_on": deps,
        "created": datetime.now().isoformat(),
        "updated": datetime.now().isoformat(),
        "completed": None,
        "estimated_hours": estimated_hours,
        "actual_hours": None
    }
    
    tasks.append(task)
    tasks = update_blocked_status(tasks)
    save_tasks(tasks)
    
    status_str = "blocked" if deps else "pending"
    print(f"[OK] Task #{task['id']} added: {title}")
    print(f"   Priority: {priority}")
    print(f"   Status: {status_str}")
    if deps:
        print(f"   Depends on: {deps}")
    return task


def list_tasks(status=None, priority=None, tag=None, show_deps=False):
    """List tasks with optional filters."""
    tasks = load_tasks()
    tasks = update_blocked_status(tasks)
    
    # Filter
    if status:
        tasks = [t for t in tasks if t['status'] == status]
    if priority:
        tasks = [t for t in tasks if t['priority'] == priority]
    if tag:
        tasks = [t for t in tasks if tag in t.get('tags', [])]
    
    # Sort by priority and status
    tasks.sort(key=lambda t: (STATUS_ORDER.get(t['status'], 99), PRIORITY_ORDER.get(t['priority'], 99)))
    
    if not tasks:
        print("No tasks found.")
        return
    
    print(f"\n[Tasks] {len(tasks)} total\n")
    print(f"{'ID':<5} {'Status':<12} {'Priority':<10} {'Title'}")
    print("-" * 70)
    
    for task in tasks:
        status_icon = {
            "pending": "[ ]",
            "in-progress": "[.]",
            "done": "[x]",
            "blocked": "[!]"
        }.get(task['status'], "[?]")
        
        priority_icon = {
            "critical": "[!!!]",
            "high": "[!]",
            "medium": "[-]",
            "low": "[v]"
        }.get(task['priority'], "[?]")
        
        title = task['title'][:40] if len(task['title']) > 40 else task['title']
        print(f"{task['id']:<5} {status_icon:<12} {priority_icon:<10} {title}")
        
        if show_deps and task.get('depends_on'):
            print(f"      Depends on: {task['depends_on']}")
        if task.get('blocked_by'):
            print(f"      Blocked by: {task['blocked_by']}")
    
    print()


def show_queue():
    """Show task queue (ready to work on, sorted by priority)."""
    tasks = load_tasks()
    tasks = update_blocked_status(tasks)
    
    # Get ready tasks (pending or in-progress, not blocked)
    ready = [t for t in tasks if t['status'] in ['pending', 'in-progress']]
    ready.sort(key=lambda t: (PRIORITY_ORDER.get(t['priority'], 99), t['created']))
    
    if not ready:
        print("\n[Queue] No ready tasks. All done or blocked!\n")
        return
    
    print(f"\n[Queue] {len(ready)} tasks ready\n")
    print(f"{'#':<4} {'ID':<5} {'Priority':<10} {'Title'}")
    print("-" * 60)
    
    for i, task in enumerate(ready[:10], 1):
        p_icon = {"critical": "!!!", "high": "!", "medium": "-", "low": "v"}.get(task['priority'], "?")
        title = task['title'][:35] if len(task['title']) > 35 else task['title']
        status_icon = "●" if task['status'] == 'in-progress' else "○"
        print(f"{i:<4} {task['id']:<5} [{p_icon}] {status_icon} {title}")
    
    if len(ready) > 10:
        print(f"\n... and {len(ready) - 10} more")
    print()


def start_next():
    """Start the next task from the queue."""
    tasks = load_tasks()
    tasks = update_blocked_status(tasks)
    
    ready = [t for t in tasks if t['status'] == 'pending']
    ready.sort(key=lambda t: PRIORITY_ORDER.get(t['priority'], 99))
    
    if not ready:
        print("[INFO] No pending tasks available.")
        return
    
    task = ready[0]
    update_task(task['id'], status='in-progress')
    print(f"[OK] Started task #{task['id']}: {task['title']}")


def update_task(task_id, status=None, priority=None, description=None, actual_hours=None):
    """Update a task."""
    tasks = load_tasks()
    tasks = update_blocked_status(tasks)
    
    task = next((t for t in tasks if t['id'] == task_id), None)
    if not task:
        print(f"[X] Task #{task_id} not found!")
        return False
    
    if status:
        # Check dependencies before allowing status change
        if status == 'in-progress' and task.get('depends_on'):
            can_run, blocking = check_dependencies(tasks, task_id)
            if not can_run:
                print(f"[X] Cannot start task #{task_id}")
                print(f"   Blocked by: {blocking}")
                return False
        
        task['status'] = status
        if status == 'done':
            task['completed'] = datetime.now().isoformat()
            task.pop('blocked_by', None)
    
    if priority:
        task['priority'] = priority
    if description:
        task['description'] = description
    if actual_hours:
        task['actual_hours'] = actual_hours
    
    task['updated'] = datetime.now().isoformat()
    
    # Re-check all blocked tasks
    tasks = update_blocked_status(tasks)
    save_tasks(tasks)
    
    print(f"[OK] Task #{task_id} updated")
    return True


def delete_task(task_id):
    """Delete a task."""
    tasks = load_tasks()
    tasks = [t for t in tasks if t['id'] != task_id]
    tasks = update_blocked_status(tasks)
    save_tasks(tasks)
    print(f"[OK] Task #{task_id} deleted")


def show_task(task_id):
    """Show task details."""
    tasks = load_tasks()
    task = next((t for t in tasks if t['id'] == task_id), None)
    
    if not task:
        print(f"[X] Task #{task_id} not found!")
        return
    
    print(f"\n[Task #{task['id']}] {task['title']}\n")
    print(f"  Status:   {task['status']}")
    print(f"  Priority: {task['priority']}")
    print(f"  Tags:     {', '.join(task.get('tags', [])) or 'None'}")
    if task.get('depends_on'):
        print(f"  Depends:  {task['depends_on']}")
    if task.get('blocked_by'):
        print(f"  Blocked:  {task['blocked_by']}")
    if task.get('estimated_hours'):
        print(f"  Est:      {task['estimated_hours']}h")
    if task.get('actual_hours'):
        print(f"  Actual:   {task['actual_hours']}h")
    print(f"  Created:  {task['created'][:19]}")
    print(f"  Updated:  {task['updated'][:19]}")
    if task.get('description'):
        print(f"\n  Description:\n    {task['description']}")
    print()


def show_stats():
    """Show task statistics."""
    tasks = load_tasks()
    tasks = update_blocked_status(tasks)
    
    total = len(tasks)
    by_status = defaultdict(int)
    by_priority = defaultdict(int)
    
    for task in tasks:
        by_status[task['status']] += 1
        by_priority[task['priority']] += 1
    
    print("\n[Statistics]\n")
    print(f"Total: {total}")
    print("\nBy Status:")
    for status, count in sorted(by_status.items(), key=lambda x: STATUS_ORDER.get(x[0], 99)):
        bar = "█" * count
        print(f"  {status:12} {bar} {count}")
    
    print("\nBy Priority:")
    for priority, count in sorted(by_priority.items(), key=lambda x: PRIORITY_ORDER.get(x[0], 99)):
        bar = "█" * count
        print(f"  {priority:12} {bar} {count}")
    
    done = by_status.get('done', 0)
    if total > 0:
        progress = (done / total) * 100
        print(f"\nProgress: {progress:.1f}% ({done}/{total} done)")
    print()


def create_workflow(template_name, workflow_name):
    """Create tasks from a workflow template."""
    if template_name not in WORKFLOW_TEMPLATES:
        print(f"[X] Unknown template: {template_name}")
        print(f"Available: {', '.join(WORKFLOW_TEMPLATES.keys())}")
        return
    
    template = WORKFLOW_TEMPLATES[template_name]
    tasks = load_tasks()
    
    prev_id = None
    created_ids = []
    
    for i, task_def in enumerate(template['tasks']):
        task = {
            "id": get_next_id(tasks),
            "title": f"[{workflow_name}] {task_def['title']}",
            "description": f"Part of workflow: {workflow_name}",
            "priority": task_def['priority'],
            "status": "blocked" if prev_id else "pending",
            "tags": task_def.get('tags', []) + [workflow_name, template_name],
            "depends_on": [prev_id] if prev_id else None,
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
            "completed": None
        }
        
        tasks.append(task)
        created_ids.append(task['id'])
        prev_id = task['id']
    
    save_tasks(tasks)
    
    print(f"[OK] Created workflow: {workflow_name}")
    print(f"   Template: {template_name}")
    print(f"   Tasks: {len(created_ids)}")
    print(f"   IDs: {created_ids}")


def show_blocked():
    """Show all blocked tasks and why."""
    tasks = load_tasks()
    tasks = update_blocked_status(tasks)
    
    blocked = [t for t in tasks if t['status'] == 'blocked']
    
    if not blocked:
        print("\n[INFO] No blocked tasks.\n")
        return
    
    print(f"\n[Blocked Tasks] {len(blocked)}\n")
    for task in blocked:
        print(f"  #{task['id']}: {task['title']}")
        if task.get('blocked_by'):
            blocking_tasks = [f"#{b}" for b in task['blocked_by']]
            print(f"      Waiting for: {', '.join(blocking_tasks)}")
        print()


def clear_done():
    """Clear all completed tasks."""
    tasks = load_tasks()
    original_count = len(tasks)
    tasks = [t for t in tasks if t['status'] != 'done']
    removed = original_count - len(tasks)
    save_tasks(tasks)
    print(f"[OK] Cleared {removed} completed tasks")


def main():
    parser = argparse.ArgumentParser(description='Task tracker v2.0')
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('title', help='Task title')
    add_parser.add_argument('--priority', '-p', default='medium',
                           choices=['critical', 'high', 'medium', 'low'])
    add_parser.add_argument('--description', '-d', help='Task description')
    add_parser.add_argument('--tags', '-t', help='Tags (comma-separated)')
    add_parser.add_argument('--depends-on', help='Depends on task IDs (comma-separated)')
    add_parser.add_argument('--est', type=float, help='Estimated hours')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List tasks')
    list_parser.add_argument('--status', choices=['pending', 'in-progress', 'done', 'blocked'])
    list_parser.add_argument('--priority', choices=['critical', 'high', 'medium', 'low'])
    list_parser.add_argument('--tag', help='Filter by tag')
    list_parser.add_argument('--deps', action='store_true', help='Show dependencies')
    
    # Queue command
    subparsers.add_parser('queue', help='Show task queue')
    
    # Next command
    subparsers.add_parser('next', help='Start next task from queue')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update a task')
    update_parser.add_argument('id', type=int, help='Task ID')
    update_parser.add_argument('--status', choices=['pending', 'in-progress', 'done', 'blocked'])
    update_parser.add_argument('--priority', choices=['critical', 'high', 'medium', 'low'])
    update_parser.add_argument('--description', help='New description')
    update_parser.add_argument('--actual', type=float, help='Actual hours spent')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a task')
    delete_parser.add_argument('id', type=int, help='Task ID')
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show task details')
    show_parser.add_argument('id', type=int, help='Task ID')
    
    # Stats command
    subparsers.add_parser('stats', help='Show statistics')
    
    # Workflow command
    workflow_parser = subparsers.add_parser('workflow', help='Create from template')
    workflow_parser.add_argument('--template', required=True,
                                choices=list(WORKFLOW_TEMPLATES.keys()),
                                help='Template name')
    workflow_parser.add_argument('--name', required=True, help='Workflow instance name')
    
    # Blocked command
    subparsers.add_parser('blocked', help='Show blocked tasks')
    
    # Clear command
    subparsers.add_parser('clear-done', help='Clear completed tasks')
    
    args = parser.parse_args()
    
    if args.command == 'add':
        tags = [t.strip() for t in args.tags.split(',')] if args.tags else []
        add_task(args.title, args.priority, args.description or "", tags, args.depends_on, args.est)
    elif args.command == 'list':
        list_tasks(args.status, args.priority, args.tag, args.deps)
    elif args.command == 'queue':
        show_queue()
    elif args.command == 'next':
        start_next()
    elif args.command == 'update':
        update_task(args.id, args.status, args.priority, args.description, args.actual)
    elif args.command == 'delete':
        delete_task(args.id)
    elif args.command == 'show':
        show_task(args.id)
    elif args.command == 'stats':
        show_stats()
    elif args.command == 'workflow':
        create_workflow(args.template, args.name)
    elif args.command == 'blocked':
        show_blocked()
    elif args.command == 'clear-done':
        clear_done()
    else:
        show_queue()


if __name__ == '__main__':
    main()
