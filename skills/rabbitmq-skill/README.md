# RabbitMQ Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Category: Messaging](https://img.shields.io/badge/category-messaging-green.svg)]()

Professional RabbitMQ message queue operations for Kimi Code CLI.

## Features

- **Queue Management**: Declare, delete, purge, and bind queues
- **Exchange Operations**: Direct, fanout, topic, headers exchanges
- **Reliable Publishing**: Publisher confirms, mandatory, persistence
- **Flexible Consuming**: Push/pull modes, manual ack, batch consume
- **RPC Pattern**: Request-reply synchronous calls
- **Dead Letter Handling**: DLX configuration for failed messages

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

```python
from rabbitmq_skill import RabbitMQSkill

# Initialize
skill = RabbitMQSkill(host="localhost", username="guest", password="guest")

# Declare a queue
from rabbitmq_skill import QueueConfig
config = QueueConfig(name="tasks", durable=True)
skill.queue_manager().declare(config)

# Publish a message
skill.publisher().send_to_queue("tasks", {"task": "send_email"})

# Consume messages
message = skill.consumer().consume_one("tasks")
if message:
    print(message["body"])
    # Acknowledge
    skill.consumer().ack(message["channel"], message["delivery_tag"])
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| host | string | Yes | RabbitMQ server host |
| port | integer | No | RabbitMQ port (default: 5672) |
| username | string | No | Username (default: guest) |
| password | string | No | Password (default: guest) |
| virtual_host | string | No | Virtual host (default: /) |

## Commands

| Command | Description |
|---------|-------------|
| declare_queue | Create a new queue |
| delete_queue | Remove a queue |
| declare_exchange | Create an exchange |
| bind | Bind queue to exchange |
| publish | Send a message |
| consume | Receive messages |

## Best Practices

1. **Use Durable Queues**: For production workloads
2. **Enable Publisher Confirms**: Already enabled by default
3. **Manual Acknowledgment**: For reliable processing
4. **Set QoS Prefetch**: Prevent consumer overload
5. **Handle Connection Errors**: Use retry logic

## FAQ

**Q: How to handle message ordering?**  
A: Use single queue with single consumer for strict ordering.

**Q: What's the recommended exchange type?**  
A: Topic for flexibility, Direct for simple routing, Fanout for broadcast.

## Changelog

### v1.0.0
- Initial release with full RabbitMQ support
- Queue, exchange, publish, consume operations
- RPC pattern implementation
