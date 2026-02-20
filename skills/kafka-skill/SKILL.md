---
name: kafka-skill
description: Apache Kafka message queue operations including topic management, producer/consumer patterns, consumer groups, and stream processing. Use when working with Kafka clusters, implementing event-driven architectures, managing message streams, or building scalable data pipelines.
---

# Kafka Skill

**Apache Kafka** 消息队列专业技能，提供完整的Topic管理、Producer/Consumer操作和消费者组管理功能。

---

## Use When

- 需要创建、删除或管理Kafka Topic
- 实现生产者发送消息到Kafka
- 实现消费者从Kafka订阅消息
- 管理消费者组和偏移量
- 监控Kafka集群健康状态
- 构建事件驱动架构
- 实现流数据处理管道

## Out of Scope

- 不处理Kafka Connect配置管理
- 不实现Kafka Streams应用程序
- 不提供Kafka集群安装部署
- 不管理Kafka ACL和安全策略
- 不处理Schema Registry集成

---

## 核心能力

| 功能模块 | 描述 | 适用场景 |
|---------|------|---------|
| **Topic管理** | 创建、删除、列示、描述Topic | 主题生命周期管理 |
| **Producer操作** | 同步/异步发送、批量发送、压缩 | 消息生产 |
| **Consumer操作** | 简单消费、消费者组、手动偏移 | 消息消费 |
| **集群管理** | 健康检查、分区管理、配置 | 运维监控 |

---

## 使用方法

### 基础用法

```python
from kafka_skill import KafkaSkill

# 初始化技能
skill = KafkaSkill(bootstrap_servers="localhost:9092")

# 检查集群健康
health = skill.health_check()
print(health)
```

### Topic管理

```python
from kafka_skill import TopicConfig

# 创建Topic
topic_config = TopicConfig(
    name="my-topic",
    num_partitions=3,
    replication_factor=1
)
result = skill.topic_manager().create_topic(topic_config)

# 列示所有Topic
topics = skill.topic_manager().list_topics()

# 删除Topic
result = skill.topic_manager().delete_topic("my-topic")
```

### Producer操作

```python
# 发送单条消息
result = skill.producer().send(
    topic="my-topic",
    value={"key": "value", "timestamp": "2026-01-01"},
    key="partition-key"
)

# 批量发送
for i in range(100):
    skill.producer().send_async(
        topic="my-topic",
        value={"index": i, "data": f"message-{i}"}
    )

# 确保所有消息发送完成
skill.producer().flush()
```

### Consumer操作

```python
# 创建消费者（自动提交偏移量）
consumer = skill.consumer(
    topics=["my-topic"],
    group_id="my-consumer-group",
    auto_offset_reset="latest"
)

# 消费消息
messages = consumer.consume(timeout_ms=5000, max_records=10)
for msg in messages:
    print(f"Topic: {msg['topic']}, Value: {msg['value']}")

# 持续消费（迭代器模式）
for msg in consumer.consume_iter(timeout_ms=1000):
    process_message(msg)
    if should_stop():
        consumer.stop()
        break
```

### 消费者组管理

```python
# 手动提交偏移量
consumer = skill.consumer(
    topics=["my-topic"],
    group_id="manual-commit-group",
    enable_auto_commit=False
)

messages = consumer.consume(timeout_ms=5000)
for msg in messages:
    process_message(msg)
    # 处理成功后手动提交
    consumer.commit()

# 暂停/恢复分区消费
from kafka.structs import TopicPartition
tp = TopicPartition("my-topic", 0)
consumer.pause([tp])
# ... 某些操作 ...
consumer.resume([tp])
```

---

## 高级功能

### 自定义序列化

```python
import pickle

# 使用Pickle序列化
producer = skill.producer(
    value_serializer=lambda v: pickle.dumps(v)
)

# 对应的消费者
def pickle_deserializer(value):
    return pickle.loads(value)

consumer = skill.consumer(
    topics=["my-topic"],
    group_id="pickle-group",
    value_deserializer=pickle_deserializer
)
```

### 生产确认级别

```python
# acks="0" - 不等待确认（最快，可能丢失消息）
# acks="1" - 等待leader确认（平衡）
# acks="all" - 等待所有副本确认（最安全，默认）

producer = skill.producer(acks="all", retries=5)
```

### 批量发送优化

```python
producer = skill.producer(
    batch_size=32768,      # 增大批量大小
    linger_ms=10,          # 等待时间聚合消息
    compression_type="gzip" # 启用压缩
)
```

---

## CLI使用

```bash
# 列示所有Topic
python -m kafka_skill --action list_topics --bootstrap-servers localhost:9092

# 创建Topic
python -m kafka_skill --action create_topic --topic my-topic

# 发送消息
python -m kafka_skill --action produce --topic my-topic --message "Hello Kafka"

# 消费消息
python -m kafka_skill --action consume --topic my-topic --group-id my-group
```

---

## 错误处理

```python
from kafka.errors import KafkaError, TopicAlreadyExistsError

result = skill.topic_manager().create_topic(config)
if not result["success"]:
    if result["error"] == "Topic already exists":
        print("Topic已存在，跳过创建")
    else:
        raise KafkaError(result["error"])
```

---

## 版本信息

- **Version**: 1.0.0
- **Author**: godlike-kimi-skills
- **License**: MIT
- **Requirements**: kafka-python>=2.0.2
