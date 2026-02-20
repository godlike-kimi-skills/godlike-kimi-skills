# Apache Kafka Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Category: Messaging](https://img.shields.io/badge/category-messaging-green.svg)]()

Professional Apache Kafka message queue operations for Kimi Code CLI.

## Features

- **Topic Management**: Create, delete, list, and describe Kafka topics
- **Producer Operations**: Sync/async message sending with batching and compression
- **Consumer Operations**: Simple consumption and consumer group management
- **Cluster Health**: Built-in health checks and monitoring
- **Flexible Serialization**: JSON, custom serializers supported
- **Error Handling**: Comprehensive error handling and retry logic

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

```python
from kafka_skill import KafkaSkill

# Initialize
skill = KafkaSkill(bootstrap_servers="localhost:9092")

# Create a topic
from kafka_skill import TopicConfig
config = TopicConfig(name="events", num_partitions=3, replication_factor=1)
skill.topic_manager().create_topic(config)

# Send a message
skill.producer().send("events", {"user": "alice", "action": "login"})

# Consume messages
consumer = skill.consumer(["events"], group_id="my-app")
messages = consumer.consume(timeout_ms=5000)
for msg in messages:
    print(msg["value"])
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| bootstrap_servers | string | Yes | Kafka broker addresses |
| topic | string | Context | Topic name for operations |
| action | string | Yes | Operation type |
| group_id | string | Consumer | Consumer group identifier |

## Commands

| Command | Description |
|---------|-------------|
| create_topic | Create a new Kafka topic |
| delete_topic | Delete an existing topic |
| list_topics | List all topics |
| produce | Send message to topic |
| consume | Receive messages from topic |

## Best Practices

1. **Use Consumer Groups**: For scalable consumption across multiple instances
2. **Enable Compression**: Use gzip/snappy for better throughput
3. **Proper Error Handling**: Always check operation results
4. **Resource Cleanup**: Call `close_all()` when done

## FAQ

**Q: How to handle message ordering?**  
A: Use the same partition key for messages that need ordering.

**Q: What's the recommended consumer group strategy?**  
A: One consumer group per application/service.

## Changelog

### v1.0.0
- Initial release with full Kafka operations support
- Topic management, producer/consumer patterns
- Consumer group management
