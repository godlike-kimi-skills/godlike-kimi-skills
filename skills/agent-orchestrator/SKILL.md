---
name: agent-orchestrator
version: 1.2
description: Agent orchestration with load balancing, auto-scaling, and health checks.
---

# Agent Orchestrator v1.2

**Intelligent agent management with load balancing and automatic health monitoring.**

## What's New in v1.2
- Added load balancing across agent pools
- Implemented agent health checks
- Added automatic agent recycling

## Features

- **Load Balancing**: Distribute tasks evenly
- **Auto Scaling**: Adjust agent count based on workload
- **Health Checks**: Monitor agent status
- **Agent Recycling**: Restart unhealthy agents
- **Pool Management**: Organize agents by capability

## Usage

### Spawn Agent

```bash
python D:/kimi/skills/agent-orchestrator/scripts/orch.py spawn \
  --task "analyze-code" \
  --priority high
```

### List Active Agents

```bash
python D:/kimi/skills/agent-orchestrator/scripts/orch.py list

# Detailed view
python D:/kimi/skills/agent-orchestrator/scripts/orch.py list --verbose
```

### Check Agent Health

```bash
python D:/kimi/skills/agent-orchestrator/scripts/orch.py health
```

### Balance Load

```bash
python D:/kimi/skills/agent-orchestrator/scripts/orch.py rebalance
```

## Agent Pools

```python
pools = {
    "general": {"max": 8, "capability": "*"},
    "coding": {"max": 4, "capability": "code"},
    "research": {"max": 2, "capability": "search"},
    "io": {"max": 4, "capability": "file,network"}
}
```

## Load Balancing Strategies

1. **Round Robin** - Equal distribution (default)
2. **Least Loaded** - Send to least busy agent
3. **Capability Match** - Match task to agent skills
4. **Priority Queue** - High priority tasks first

## Auto-Scaling Rules

```python
scaling_rules = {
    "scale_up": {
        "condition": "queue_depth > 5",
        "max_agents": 12
    },
    "scale_down": {
        "condition": "idle_agents > 3",
        "min_agents": 1
    }
}
```

## Health Check Configuration

```toml
[health_check]
interval = 30          # Check every 30 seconds
timeout = 10           # Response timeout
unhealthy_threshold = 3  # Mark unhealthy after 3 failures
recovery_threshold = 2   # Mark healthy after 2 successes
```

## Concurrency Limits

```python
MAX_CONCURRENT_AGENTS = 12  # Based on 16 cores - 4 reserve
MAX_AGENTS_PER_POOL = 8
DEFAULT_AGENT_TIMEOUT = 300  # 5 minutes
```

## Best Practices

- ✅ Max 12 concurrent agents (16 cores - 4 reserve)
- ✅ Use round-robin for equal priority tasks
- ✅ Monitor agent output size
- ✅ Recycle agents after N tasks
- ✅ Implement graceful shutdown

## Integration

### With Task Tracker

```python
# Orchestrator receives tasks from tracker
for task in task_tracker.pending_tasks:
    if orchestrator.can_accept_task():
        orchestrator.assign_task(task)
```

### With System Monitor

```python
# Check resources before spawning
if system_monitor.can_spawn():
    orchestrator.spawn_agent(task)
```
