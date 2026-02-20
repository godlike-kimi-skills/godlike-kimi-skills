---
name: celery-skill
description: Celery distributed task queue operations including task definition, worker management, periodic tasks, chains, groups, chords, and result backends. Use when building distributed task systems, scheduling periodic jobs, or implementing complex task workflows.
---

# Celery Skill

**Celery** 分布式任务队列专业技能，提供完整的任务管理、Worker管理、定时任务和复杂工作流功能。

---

## Use When

- 需要实现异步任务处理
- 构建分布式任务系统
- 需要定时/周期性任务调度
- 实现复杂任务工作流(链式、并行、回调)
- 需要任务结果追踪和查询
- 管理Worker集群
- 需要任务重试和错误处理

## Out of Scope

- 不提供Celery Worker安装部署
- 不处理底层Broker(需要单独安装Redis/RabbitMQ)
- 不提供Flower监控界面配置
- 不实现自定义Result Backend开发
- 不处理任务信号和事件的高级定制

---

## 核心能力

| 功能模块 | 描述 | 适用场景 |
|---------|------|---------|
| **任务管理** | 发送任务、撤销、结果查询 | 异步执行 |
| **Worker管理** | 检查状态、控制操作 | 集群管理 |
| **工作流** | Chain/Group/Chord/Map | 复杂流程 |
| **定时任务** | Crontab/Interval调度 | 周期性任务 |
| **结果追踪** | 异步结果、状态查询 | 任务监控 |

---

## 使用方法

### 基础用法

```python
from celery_skill import CelerySkill

# 初始化技能
skill = CelerySkill(
    broker_url="redis://localhost:6379/0",
    result_backend="redis://localhost:6379/0"
)

# 检查健康状态
health = skill.health_check()
print(health)
```

### 发送任务

```python
# 基本任务发送
result = skill.task_manager().send_task(
    task_name="myapp.tasks.send_email",
    args=("user@example.com", "Welcome!"),
    kwargs={"template": "welcome"}
)
task_id = result["task_id"]

# 延迟执行（countdown）
result = skill.task_manager().send_task(
    task_name="myapp.tasks.cleanup",
    countdown=3600  # 1小时后执行
)

# 指定执行时间（eta）
from datetime import datetime, timedelta
eta = datetime.now() + timedelta(minutes=30)
result = skill.task_manager().send_task(
    task_name="myapp.tasks.reminder",
    eta=eta
)

# 设置过期时间
result = skill.task_manager().send_task(
    task_name="myapp.tasks.notify",
    expires=3600  # 1小时内必须执行，否则丢弃
)

# 指定队列和优先级
result = skill.task_manager().send_task(
    task_name="myapp.tasks.process",
    args=(data,),
    queue="high-priority",
    priority=9
)

# 重试配置
result = skill.task_manager().send_task(
    task_name="myapp.tasks.api_call",
    retries=3,
    retry_delay=60  # 重试间隔60秒
)
```

### 查询任务结果

```python
# 获取结果（非阻塞）
status = skill.task_manager().get_status(task_id)
print(f"Task status: {status['status']}")

# 获取结果（阻塞等待）
result = skill.task_manager().get_result(task_id, timeout=30)
if result["success"]:
    print(f"Result: {result['result']}")
else:
    print(f"Error: {result.get('error')}")

# 获取已完成的任务结果（不等待）
result = skill.task_manager().get_result(task_id)
print(f"Ready: {result['ready']}, Status: {result['status']}")
```

### 撤销任务

```python
# 撤销未执行的任务
skill.task_manager().revoke(task_id)

# 终止正在执行的任务
skill.task_manager().revoke(
    task_id,
    terminate=True,
    signal="SIGTERM"
)

# 立即终止（强制）
skill.task_manager().revoke(
    task_id,
    terminate=True,
    signal="SIGKILL"
)
```

### Worker管理

```python
# 检查所有Worker状态
workers = skill.worker_manager().inspect_workers()
for worker in workers["workers"]:
    print(f"Worker: {worker['hostname']}")
    print(f"Active tasks: {len(worker['active_tasks'])}")
    print(f"Processed: {worker['stats'].get('total', {}).get('tasks', 0)}")

# Ping所有Worker
ping = skill.worker_manager().ping_workers()
print(f"Active workers: {ping['active_workers']}")

# 获取正在执行的任务
active = skill.worker_manager().get_active_tasks()
for task in active["tasks"]:
    print(f"Worker: {task['worker']}, Task: {task['name']}, ID: {task['id']}")

# 获取已注册的所有任务
registered = skill.worker_manager().get_registered_tasks()
print(f"Available tasks: {registered['tasks']}")

# 重启Worker Pool
skill.worker_manager().pool_restart()

# 优雅关闭Worker
skill.worker_manager().shutdown_workers()
```

### 工作流模式

```python
# Chain - 串行执行
# task1 -> task2 -> task3 (task2接收task1的结果)
result = skill.workflow().chain_tasks(
    ("tasks.extract", (url,)),
    ("tasks.transform",),  # 接收extract的结果
    ("tasks.load",)        # 接收transform的结果
)

# Group - 并行执行
# 所有任务同时执行，等待全部完成
result = skill.workflow().group_tasks(
    ("tasks.process_image", ("img1.jpg",)),
    ("tasks.process_image", ("img2.jpg",)),
    ("tasks.process_image", ("img3.jpg",))
)

# Chord - 并行+回调
# 所有header任务完成后，执行callback
result = skill.workflow().chord_workflow(
    header_tasks=[
        ("tasks.fetch_data", ("source1",)),
        ("tasks.fetch_data", ("source2",)),
        ("tasks.fetch_data", ("source3",))
    ],
    callback_task=("tasks.aggregate",)  # 接收所有header结果列表
)

# Map - 批量映射
# 对列表中的每个元素执行相同任务
items = [(1,), (2,), (3,), (4,), (5,)]
result = skill.workflow().map_task(
    task_name="tasks.square",
    items=items,
    chord_callback="tasks.sum_results"  # 可选：汇总回调
)
```

### 定时任务调度

```python
from datetime import timedelta

# 间隔调度（每30秒）
skill.scheduler().add_periodic_task(
    task_name="tasks.check_health",
    schedule=30.0,
    name="health-check-30s"
)

# 使用timedelta
skill.scheduler().add_periodic_task(
    task_name="tasks.cleanup",
    schedule=timedelta(hours=1),
    args=("/tmp",),
    name="hourly-cleanup"
)

# Crontab调度
# 每天凌晨2点执行
skill.scheduler().add_periodic_task(
    task_name="tasks.daily_report",
    schedule=skill.scheduler().crontab(hour=2, minute=0),
    name="daily-report"
)

# 每周一上午9点
skill.scheduler().add_periodic_task(
    task_name="tasks.weekly_summary",
    schedule=skill.scheduler().crontab(
        day_of_week=1,  # Monday
        hour=9,
        minute=0
    ),
    name="weekly-summary"
)

# 每月1号
skill.scheduler().add_periodic_task(
    task_name="tasks.monthly_cleanup",
    schedule=skill.scheduler().crontab(
        day_of_month=1,
        hour=0,
        minute=0
    ),
    name="monthly-cleanup"
)

# 复杂Crontab（工作日每15分钟）
skill.scheduler().add_periodic_task(
    task_name="tasks.poll_api",
    schedule=skill.scheduler().crontab(
        day_of_week="1-5",  # Monday to Friday
        minute="*/15"       # Every 15 minutes
    ),
    name="weekday-polling"
)
```

### 注册任务函数

```python
# 定义任务函数
def send_email(to: str, subject: str, body: str):
    # 实际发送邮件逻辑
    return {"sent": True, "to": to}

def process_data(data: dict):
    # 数据处理逻辑
    result = data.copy()
    result["processed"] = True
    return result

# 注册为Celery任务
skill.register_task(send_email, name="tasks.send_email")
skill.register_task(process_data, name="tasks.process_data")

# 现在可以通过名称调用
result = skill.task_manager().send_task(
    "tasks.send_email",
    args=("user@example.com", "Hello", "Welcome!")
)
```

---

## 高级功能

### 任务结果后端配置

```python
# Redis结果后端
skill = CelerySkill(
    broker_url="redis://localhost:6379/0",
    result_backend="redis://localhost:6379/1"
)

# RPC结果后端（临时队列）
skill = CelerySkill(
    broker_url="amqp://guest:guest@localhost:5672//",
    result_backend="rpc://"
)
```

### 任务重试策略

```python
# 指数退避重试
result = skill.task_manager().send_task(
    task_name="tasks.unreliable_api",
    retries=5,
    retry_delay=10,  # 第一次重试等待10秒
    # 后续重试: 20s, 40s, 80s, 160s (指数增长)
)

# 使用Retry-After头
# Celery会自动遵守服务端返回的Retry-After
```

### 工作流结果处理

```python
# Chain结果
chain_result = skill.workflow().chain_tasks(
    ("tasks.step1", ("input",)),
    ("tasks.step2",),
    ("tasks.step3",)
)

# 获取最终结果
final_result = skill.task_manager().get_result(
    chain_result.id,
    timeout=60
)

# Group结果
group_result = skill.workflow().group_tasks(
    ("tasks.task1",),
    ("tasks.task2",),
    ("tasks.task3",)
)

# 等待所有任务完成
while not group_result.ready():
    time.sleep(1)

# 获取每个任务的结果
for i, result in enumerate(group_result.results):
    print(f"Task {i}: {result.get()}")

# Chord回调结果
chord_result = skill.workflow().chord_workflow(
    header_tasks=[("tasks.t1",), ("tasks.t2",)],
    callback_task=("tasks.callback",)
)
# callback接收 [t1_result, t2_result]
```

---

## CLI使用

```bash
# 发送任务
python -m celery_skill --action send_task --task-name tasks.email --args '["user@example.com", "Hello"]'

# 查询结果
python -m celery_skill --action get_result --task-id abc-123-def

# 检查Workers
python -m celery_skill --action inspect_workers

# Ping Workers
python -m celery_skill --action ping

# 健康检查
python -m celery_skill --action health
```

---

## 架构模式

### 简单异步模式

```
Web App -> send_task -> Broker -> Worker -> execute
                            |
                            v
                        Result Backend
```

### 分布式工作流模式

```
                    -> Worker 1 -> Task A
                   /
Dispatcher -> Broker -> Worker 2 -> Task B -> Callback
                   \
                    -> Worker 3 -> Task C
```

### 定时任务模式

```
Scheduler (Beat) -> Broker -> Worker -> execute
```

---

## 最佳实践

1. **任务幂等性**: 设计任务可以安全地多次执行
2. **任务粒度**: 保持任务小而专注，便于重试
3. **超时设置**: 为任务设置合理的time_limit
4. **结果过期**: 配置result_expires避免结果堆积
5. **队列分离**: 按优先级/类型使用不同队列
6. **Worker数量**: 根据CPU核心数设置concurrency

---

## 版本信息

- **Version**: 1.0.0
- **Author**: godlike-kimi-skills
- **License**: MIT
- **Requirements**: celery>=5.3.6, redis>=5.0.1
