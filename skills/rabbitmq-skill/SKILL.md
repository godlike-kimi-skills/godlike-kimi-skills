---
name: rabbitmq-skill
description: RabbitMQ message queue operations including queue management, exchanges, routing patterns, RPC, and dead letter handling. Use when working with RabbitMQ brokers, implementing message routing patterns, building microservices communication, or setting up reliable message delivery systems.
---

# RabbitMQ Skill

**RabbitMQ** 消息队列专业技能，提供完整的队列管理、Exchange操作、路由模式、RPC调用和死信处理功能。

---

## Use When

- 需要创建、删除或管理RabbitMQ队列
- 实现Exchange声明和队列绑定
- 使用不同的路由模式(direct/fanout/topic/headers)
- 发送和接收消息
- 实现RPC远程调用模式
- 配置死信队列处理失败消息
- 构建微服务间通信

## Out of Scope

- 不处理RabbitMQ集群安装部署
- 不提供Shovel/Federation配置
- 不实现MQTT/STOMP协议
- 不管理RabbitMQ用户权限
- 不处理镜像队列配置

---

## 核心能力

| 功能模块 | 描述 | 适用场景 |
|---------|------|---------|
| **队列管理** | 声明、删除、清空、绑定队列 | 队列生命周期 |
| **Exchange管理** | Direct/Fanout/Topic/Headers类型 | 消息路由 |
| **消息发布** | 可靠发布、持久化、TTL、优先级 | 消息发送 |
| **消息消费** | 推/拉模式、手动Ack、批量消费 | 消息接收 |
| **RPC模式** | 请求-响应同步调用 | 远程调用 |

---

## 使用方法

### 基础用法

```python
from rabbitmq_skill import RabbitMQSkill

# 初始化技能
skill = RabbitMQSkill(
    host="localhost",
    port=5672,
    username="guest",
    password="guest"
)

# 检查连接健康
health = skill.health_check()
print(health)
```

### 队列管理

```python
from rabbitmq_skill import QueueConfig

# 声明队列（持久化）
config = QueueConfig(
    name="my-queue",
    durable=True,
    auto_delete=False
)
result = skill.queue_manager().declare(config)

# 声明带TTL的队列
config_ttl = QueueConfig(
    name="ttl-queue",
    durable=True,
    message_ttl=60000  # 60秒过期
)
skill.queue_manager().declare(config_ttl)

# 声明死信队列
dlq_config = QueueConfig(
    name="main-queue",
    durable=True,
    dead_letter_exchange="dlx",
    dead_letter_routing_key="dlq"
)
skill.queue_manager().declare(dlq_config)

# 删除队列
skill.queue_manager().delete("my-queue")

# 清空队列
skill.queue_manager().purge("my-queue")
```

### Exchange管理

```python
from rabbitmq_skill import ExchangeConfig

# Direct Exchange
skill.exchange_manager().declare(
    ExchangeConfig(name="direct-ex", exchange_type="direct")
)

# Fanout Exchange (广播)
skill.exchange_manager().declare(
    ExchangeConfig(name="fanout-ex", exchange_type="fanout")
)

# Topic Exchange (模式匹配)
skill.exchange_manager().declare(
    ExchangeConfig(name="topic-ex", exchange_type="topic")
)

# 绑定队列到Exchange
skill.queue_manager().bind(
    queue_name="my-queue",
    exchange_name="direct-ex",
    routing_key="my.key"
)
```

### 消息发布

```python
# 发送到队列(默认Exchange)
skill.publisher().send_to_queue(
    queue_name="my-queue",
    body={"user": "alice", "action": "login"},
    persistent=True,  # 持久化消息
    message_id="msg-001"
)

# 发送到Exchange
skill.publisher().publish(
    exchange="topic-ex",
    routing_key="user.login",
    body={"event": "user_login"},
    persistent=True,
    headers={"source": "web"}
)

# 带过期时间的消息
skill.publisher().send_to_queue(
    queue_name="my-queue",
    body={"temp": "data"},
    expiration=30000  # 30秒后过期
)
```

### 消息消费

```python
# 单条消费
message = skill.consumer().consume_one("my-queue")
if message:
    print(f"Received: {message['body']}")
    # 手动确认
    channel = message["channel"]
    delivery_tag = message["delivery_tag"]
    skill.consumer().ack(channel, delivery_tag)

# 批量消费
messages = skill.consumer().consume_batch("my-queue", batch_size=10)
for msg in messages:
    process_message(msg['body'])

# 持续消费
def message_handler(channel, message):
    print(f"Processing: {message['body']}")
    # 处理成功后确认
    channel.basic_ack(delivery_tag=message['delivery_tag'])

skill.consumer(prefetch_count=5).start_consuming(
    queue_name="my-queue",
    callback=message_handler,
    auto_ack=False
)
```

### RPC远程调用

```python
# 客户端调用
response = skill.rpc().call(
    queue_name="rpc-queue",
    payload={"method": "add", "args": [1, 2]},
    timeout=30
)
print(response)  # {"result": 3}
```

---

## 高级功能

### 可靠发布模式

```python
# Publisher Confirm模式已默认启用
result = skill.publisher().publish(
    exchange="my-ex",
    routing_key="key",
    body="important message",
    mandatory=True  # 如果无法路由则返回错误
)

if not result["success"]:
    # 处理发布失败
    handle_publish_failure(result["error"])
```

### 消费QoS配置

```python
# prefetch_count控制未确认消息数量
consumer = skill.consumer(prefetch_count=10, auto_ack=False)

# 适用于工作队列，确保公平分发
```

### 死信队列模式

```python
# 1. 声明死信Exchange和队列
skill.exchange_manager().declare(
    ExchangeConfig(name="dlx", exchange_type="topic")
)
skill.queue_manager().declare(
    QueueConfig(name="dlq", durable=True)
)
skill.queue_manager().bind("dlq", "dlx", "#")

# 2. 声明主队列，设置死信参数
skill.queue_manager().declare(
    QueueConfig(
        name="main-queue",
        durable=True,
        message_ttl=30000,  # 消息30秒过期
        max_length=1000,    # 最大1000条消息
        dead_letter_exchange="dlx",
        dead_letter_routing_key="dlq"
    )
)
```

---

## CLI使用

```bash
# 检查健康状态
python -m rabbitmq_skill --action health --host localhost

# 声明队列
python -m rabbitmq_skill --action declare_queue --queue my-queue

# 发送消息
python -m rabbitmq_skill --action publish --queue my-queue --message "Hello"

# 消费单条消息
python -m rabbitmq_skill --action consume_one --queue my-queue
```

---

## 常见路由模式

### Direct Routing

```python
# 精确匹配routing_key
skill.publisher().publish("direct-ex", "error", {"msg": "error occurred"})
skill.queue_manager().bind("error-queue", "direct-ex", "error")
```

### Fanout Broadcasting

```python
# 广播到所有绑定队列
skill.exchange_manager().declare(ExchangeConfig("logs", "fanout"))
skill.queue_manager().bind("log-queue1", "logs", "")  # 忽略routing_key
skill.queue_manager().bind("log-queue2", "logs", "")
```

### Topic Pattern Matching

```python
# 使用通配符: * 匹配一个单词, # 匹配零个或多个
skill.publisher().publish("topic-ex", "user.login.success", {})
skill.publisher().publish("topic-ex", "user.logout", {})

skill.queue_manager().bind("user-events", "topic-ex", "user.*")
skill.queue_manager().bind("all-events", "topic-ex", "#")
```

---

## 错误处理

```python
from pika.exceptions import AMQPConnectionError, ChannelClosed

try:
    skill = RabbitMQSkill(host="localhost")
    result = skill.queue_manager().declare(QueueConfig("test"))
    if not result["success"]:
        print(f"Declaration failed: {result['error']}")
except AMQPConnectionError as e:
    print(f"Connection failed: {e}")
finally:
    skill.close()
```

---

## 版本信息

- **Version**: 1.0.0
- **Author**: godlike-kimi-skills
- **License**: MIT
- **Requirements**: pika>=1.3.2
