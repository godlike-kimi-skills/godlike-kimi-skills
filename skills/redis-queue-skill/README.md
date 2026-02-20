# Redis Queue Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Category: Messaging](https://img.shields.io/badge/category-messaging-green.svg)]()

Professional Redis queue operations for Kimi Code CLI.

## Features

- **List Queues**: FIFO/LIFO operations with blocking support
- **Redis Streams**: Event sourcing with consumer groups
- **Pub/Sub**: Real-time messaging patterns
- **Priority Queues**: Sorted set-based priority handling
- **Task Queues**: Delayed execution with retry logic
- **Distributed**: Works across multiple workers

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

```python
from redis_queue_skill import RedisQueueSkill

# Initialize
skill = RedisQueueSkill(host="localhost", port=6379)

# List queue (FIFO)
skill.list_queue().push_right("tasks", {"job": "process_data"})
task = skill.list_queue().pop_left("tasks")

# Streams
skill.stream().add("events", {"user": "alice", "action": "login"})
entries = skill.stream().range("events")

# Pub/Sub
skill.pubsub().publish("updates", {"type": "notification"})
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| host | string | Yes | Redis server host |
| port | integer | No | Redis port (default: 6379) |
| db | integer | No | Database number (default: 0) |
| password | string | No | Authentication password |

## Commands

| Command | Description |
|---------|-------------|
| lpush | Push to left side of list |
| rpush | Push to right side of list |
| lpop | Pop from left side |
| rpop | Pop from right side |
| xadd | Add entry to stream |
| xread | Read from stream |
| publish | Publish message |
| subscribe | Subscribe to channel |

## Best Practices

1. **Use Blocking Operations**: BRPOP/BLPOP instead of polling
2. **Stream Maxlen**: Set limit to prevent memory issues
3. **Consumer Groups**: For distributed processing
4. **Retry Logic**: Implement in task queue
5. **Health Checks**: Monitor connection status

## FAQ

**Q: List vs Stream - which to use?**  
A: Use Lists for simple queues, Streams for event sourcing and consumer groups.

**Q: Can messages be lost with Pub/Sub?**  
A: Yes, Pub/Sub doesn't persist messages. Use Streams for persistence.

## Changelog

### v1.0.0
- Initial release with Redis queue operations
- List, Stream, Pub/Sub, Priority Queue, Task Queue support
