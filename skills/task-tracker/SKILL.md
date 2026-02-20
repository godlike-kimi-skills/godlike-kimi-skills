---
name: task-tracker
version: 2.1
description: Task management with DAG dependencies, workflow templates, and enhanced retry mechanisms.
---

# Task Tracker v2.1

**Advanced task management with dependency resolution and automatic retry.**

## What's New in v2.1
- Added task priority inheritance
- Implemented deadlock detection for task dependencies
- Added task retry with exponential backoff

## Features

- **DAG Dependencies**: Define complex task workflows
- **Priority Queue**: High-priority tasks execute first
- **Auto Retry**: Exponential backoff on failure
- **Deadlock Detection**: Prevent circular dependencies
- **Progress Tracking**: Real-time task status

## Usage

### Create Task

```bash
python D:/kimi/skills/task-tracker/scripts/task.py create \
  --name "analyze-data" \
  --priority high \
  --workflow "data-analysis"
```

### Define Dependencies (DAG)

```bash
# Task B depends on Task A
python D:/kimi/skills/task-tracker/scripts/task.py depend \
  --task "task-B" \
  --on "task-A"

# Multiple dependencies
python D:/kimi/skills/task-tracker/scripts/task.py depend \
  --task "deploy" \
  --on "build,test,lint"
```

### Execute Workflow

```bash
python D:/kimi/skills/task-tracker/scripts/task.py execute \
  --workflow "data-analysis" \
  --parallel 4
```

### Check Task Status

```bash
python D:/kimi/skills/task-tracker/scripts/task.py status

# Detailed view
python D:/kimi/skills/task-tracker/scripts/task.py status --verbose
```

## Workflow Templates

### Data Analysis Pipeline

```toml
[workflow.data-analysis]
tasks = ["fetch", "clean", "analyze", "report"]
dependencies = [
    "clean -> fetch",
    "analyze -> clean",
    "report -> analyze"
]
```

### CI/CD Pipeline

```toml
[workflow.ci-cd]
tasks = ["lint", "test", "build", "deploy"]
dependencies = [
    "test -> lint",
    "build -> test",
    "deploy -> build"
]
parallel = ["lint", "test"]  # Can run in parallel
```

## Task Retry Configuration

```toml
[task.retry]
max_attempts = 3
backoff_strategy = "exponential"  # exponential, linear, fixed
initial_delay = 5  # seconds
max_delay = 60     # seconds
```

## Priority Levels

1. **critical** - Execute immediately, block other tasks
2. **high** - Execute before normal tasks
3. **normal** - Standard priority (default)
4. **low** - Execute when resources available
5. **background** - Execute only when idle

## Best Practices

- ✅ Use DAG for complex workflows
- ✅ Set task timeouts per complexity
- ✅ Log all task transitions
- ✅ Handle failures gracefully
- ✅ Implement idempotent tasks

## Integration

### With Context Manager

```python
# Check context before starting new task phase
if context_monitor.should_handoff(current_tokens):
    execute_handoff()
```

### With System Monitor

```python
# Only spawn if resources available
if system_monitor.check_can_spawn():
    spawn_subagent(task)
```
