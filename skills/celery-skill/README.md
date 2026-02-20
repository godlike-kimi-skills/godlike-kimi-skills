# Celery Task Queue Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Category: Messaging](https://img.shields.io/badge/category-messaging-green.svg)]()

Professional Celery distributed task queue operations for Kimi Code CLI.

## Features

- **Task Management**: Send, revoke, retry, and query task results
- **Worker Management**: Inspect, ping, control worker pools
- **Workflow Patterns**: Chain, Group, Chord, Map primitives
- **Periodic Tasks**: Crontab and interval-based scheduling
- **Result Tracking**: Async result retrieval with timeout support
- **Distributed**: Works with Redis or RabbitMQ backends

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

```python
from celery_skill import CelerySkill

# Initialize
skill = CelerySkill(
    broker_url="redis://localhost:6379/0",
    result_backend="redis://localhost:6379/0"
)

# Send a task
result = skill.task_manager().send_task(
    "myapp.tasks.process",
    args=("data",),
    countdown=60  # Execute after 60 seconds
)

# Check result
status = skill.task_manager().get_status(result["task_id"])
print(status)
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| broker_url | string | Yes | Celery broker URL |
| result_backend | string | No | Result backend URL |
| task_name | string | Context | Task function name |
| countdown | integer | No | Delay in seconds |
| retries | integer | No | Number of retries |

## Commands

| Command | Description |
|---------|-------------|
| send_task | Send task to queue |
| get_result | Retrieve task result |
| inspect_workers | Get worker status |
| revoke_task | Cancel running task |
| apply_async | Execute with options |

## Best Practices

1. **Idempotent Tasks**: Design tasks to be safely retried
2. **Reasonable Timeouts**: Set appropriate time limits
3. **Separate Queues**: Use queues for different priorities
4. **Result Cleanup**: Configure result expiration
5. **Monitor Workers**: Regular health checks

## FAQ

**Q: What broker should I use?**  
A: Redis for simplicity, RabbitMQ for advanced routing.

**Q: How to handle task failures?**  
A: Use retries with exponential backoff, and dead letter queues.

## Changelog

### v1.0.0
- Initial release with full Celery support
- Task, worker, workflow, and scheduling operations
