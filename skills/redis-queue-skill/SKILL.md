---
name: redis-queue-skill
description: Redis queue operations including Lists, Streams, Pub/Sub patterns, priority queues, delayed tasks, and distributed task management. Use when working with Redis as a message broker, implementing task queues, real-time messaging, or building lightweight distributed systems.
---

# Redis Queue Skill

**Redis** 消息队列专业技能，提供完整的List队列、Stream流、Pub/Sub发布订阅、优先级队列和任务队列功能。

---

## Use When

- 使用Redis作为轻量级消息队列
- 实现List类型的FIFO/LIFO队列
- 使用Redis Streams进行事件溯源
- 实现Pub/Sub实时消息推送
- 构建优先级队列
- 实现延迟任务队列
- 需要分布式任务管理

## Out of Scope

- 不处理Redis集群安装部署
- 不提供Redis持久化配置管理
- 不实现复杂的事务处理
- 不管理Redis Lua脚本
- 不提供Redis Sentinel/Cluster配置

---

## 核心能力

| 功能模块 | 描述 | 适用场景 |
|---------|------|---------|
| **List队列** | LPUSH/RPOP等操作，支持阻塞 | 简单任务队列 |
| **Streams** | 事件流、消费者组 | 事件溯源、日志 |
| **Pub/Sub** | 发布订阅模式 | 实时通知 |
| **优先级队列** | Sorted Set实现 | 优先级任务 |
| **任务队列** | 延迟执行、重试机制 | 分布式任务 |

---

## 使用方法

### 基础用法

```python
from redis_queue_skill import RedisQueueSkill

# 初始化技能
skill = RedisQueueSkill(
    host="localhost",
    port=6379,
    db=0
)

# 检查连接健康
health = skill.health_check()
print(health)
```

### List队列操作

```python
# FIFO队列 (生产者-消费者)
skill.list_queue().push_right("work-queue", {"task": "email", "to": "user@example.com"})
task = skill.list_queue().pop_left("work-queue")  # 阻塞弹出

# LIFO栈
skill.list_queue().push_left("stack", "item1")
skill.list_queue().push_left("stack", "item2")
item = skill.list_queue().pop_left("stack")  # item2

# 阻塞消费 (推荐)
while True:
    message = skill.list_queue().pop_left("work-queue", timeout=5)
    if message:
        process_message(message)

# 查看队列长度
length = skill.list_queue().length("work-queue")

# 查看队列内容
items = skill.list_queue().range("work-queue", start=0, end=9)  # 前10个

# 安全队列模式 (RPOPLPUSH)
# 从queue弹出，推入processing-queue，处理完成后删除
message = skill.list_queue().pop_left_push("queue", "processing-queue")
process_message(message)
skill.list_queue().remove("processing-queue", message)
```

### Streams流操作

```python
# 添加事件到流
entry_id = skill.stream().add(
    stream_name="user-events",
    fields={"user_id": "123", "action": "login", "ip": "192.168.1.1"},
    maxlen=10000  # 保留最近10000条
)

# 读取流（从最早开始）
entries = skill.stream().range("user-events", start="-", end="+")
for entry in entries:
    print(f"ID: {entry.id}, Data: {entry.fields}")

# 阻塞读取新消息
while True:
    result = skill.stream().read(
        streams={"user-events": "$"},  # 只读新消息
        block=5000  # 阻塞5秒
    )
    for stream_name, entries in result.items():
        for entry in entries:
            process_event(entry)

# 消费者组（用于多消费者负载均衡）
skill.stream().create_consumer_group("events", "processors", mkstream=True)

# 以消费者组成员身份读取
result = skill.stream().read_group(
    group_name="processors",
    consumer_name="worker-1",
    streams={"events": ">"},  # 只读未分配给其他人的消息
    count=10
)

# 确认消息处理完成
for stream_name, entries in result.items():
    ids = [e.id for e in entries]
    skill.stream().acknowledge(stream_name, "processors", *ids)

# 查看pending消息（处理中未确认）
pending = skill.stream().pending("events", "processors")
print(pending)
```

### Pub/Sub发布订阅

```python
# 发布消息
skill.pubsub().publish("notifications", {"type": "alert", "msg": "System alert"})

# 订阅频道（异步）
import threading

def listen_notifications():
    pubsub = skill.pubsub()
    pubsub.subscribe("notifications")
    
    for message in pubsub.listen():
        if message["type"] == "message":
            print(f"Received: {message['data']}")

# 在后台线程监听
thread = threading.Thread(target=listen_notifications)
thread.start()

# 模式订阅
pubsub = skill.pubsub()
pubsub.psubscribe("user.*")  # 订阅所有user.开头的频道
for message in pubsub.listen():
    print(f"Channel: {message['channel']}, Data: {message['data']}")
```

### 优先级队列

```python
from redis_queue_skill import RedisPriorityQueue

# 添加带优先级的任务 (数字越小优先级越高)
skill.priority_queue().add("urgent-tasks", "critical-task", priority=1)
skill.priority_queue().add("urgent-tasks", "normal-task", priority=10)
skill.priority_queue().add("urgent-tasks", "low-priority", priority=100)

# 获取最高优先级任务
task, priority = skill.priority_queue().pop_min("urgent-tasks")[0]
print(f"Processing: {task} (priority: {priority})")

# 按优先级范围查询
medium_priority_tasks = skill.priority_queue().range_by_score(
    "urgent-tasks", min_score=5, max_score=50
)
```

### 任务队列（带延迟和重试）

```python
from redis_queue_skill import Task

# 创建任务队列
task_queue = skill.task_queue(prefix="email")

# 立即执行任务
task_queue.schedule(
    payload={"type": "send_email", "to": "user@example.com"},
    priority=1,
    retries=3
)

# 延迟执行任务 (10秒后执行)
task_queue.schedule(
    payload={"type": "reminder", "msg": "Meeting in 1 hour"},
    delay=3600,  # 1小时后
    retries=2
)

# 工作者处理任务
while True:
    task = task_queue.dequeue(timeout=5)
    if task:
        try:
            execute_task(task.payload)
            task_queue.complete(task, success=True)
        except Exception as e:
            logger.error(f"Task failed: {e}")
            task_queue.complete(task, success=False)  # 自动重试或进入DLQ

# 查看队列统计
stats = task_queue.get_stats()
print(f"Ready: {stats['ready']}, Delayed: {stats['delayed']}, Processing: {stats['processing']}, DLQ: {stats['dlq']}")
```

---

## 高级功能

### 使用自定义序列化

```python
import msgpack

class MsgPackRedisQueueSkill(RedisQueueSkill):
    def list_queue(self):
        queue = super().list_queue()
        queue._serialize = lambda x: msgpack.packb(x, use_bin_type=True)
        queue._deserialize = lambda x: msgpack.unpackb(x, raw=False)
        return queue
```

### 流的时间范围查询

```python
# 查询最近1小时的事件
from datetime import datetime, timedelta

one_hour_ago = datetime.now() - timedelta(hours=1)
start_id = f"{int(one_hour_ago.timestamp() * 1000)}-0"

recent_events = skill.stream().range(
    "events",
    start=start_id,
    end="+",
    count=100
)
```

### 消费者组故障恢复

```python
# 1. 查看pending消息
pending = skill.stream().pending("events", "processors")

# 2. 检查是否有长时间未确认的消息
# 3. 将超时消息转移给其他消费者
claimed = skill.stream().claim(
    stream_name="events",
    group_name="processors", 
    consumer_name="worker-2",
    min_idle_time=60000,  # 1分钟未处理
    message_ids=["1234567890-0"]
)
```

---

## CLI使用

```bash
# 检查健康状态
python -m redis_queue_skill --action health --host localhost

# 推入队列
python -m redis_queue_skill --action lpush --queue my-queue --message "Hello"

# 弹出队列
python -m redis_queue_skill --action rpop --queue my-queue

# 查看队列长度
python -m redis_queue_skill --action llen --queue my-queue

# 添加流事件
python -m redis_queue_skill --action xadd --stream events --message '{"event": "test"}'
```

---

## 架构模式

### 简单工作队列 (List)

```
Producer -> LPUSH work-queue
Worker 1 -> BRPOP work-queue
Worker 2 -> BRPOP work-queue
```

### 发布订阅 (Pub/Sub)

```
Publisher -> PUBLISH channel message
Subscriber 1 -> SUBSCRIBE channel
Subscriber 2 -> SUBSCRIBE channel
```

### 事件溯源 (Streams)

```
Service -> XADD events * field value
Consumer Group -> XREADGROUP GROUP processors worker-1
```

### 延迟任务队列

```
Task with delay -> ZADD delayed:tasks score task
Scheduler -> ZRANGEBYSCORE 0 now -> LPUSH ready:tasks
Worker -> BRPOP ready:tasks
```

---

## 性能建议

1. **List队列**: 使用BRPOP/BLPOP代替轮询
2. **Streams**: 使用消费者组实现负载均衡
3. **Pub/Sub**: 注意消息不持久化，可能丢失
4. **大列表**: 使用LRANGE分页，避免阻塞
5. **内存管理**: 设置MAXLEN限制流大小

---

## 版本信息

- **Version**: 1.0.0
- **Author**: godlike-kimi-skills
- **License**: MIT
- **Requirements**: redis>=5.0.1
