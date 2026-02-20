# Cron Skill

Cron表达式工具，支持表达式生成、验证、下次执行时间计算。

## Use When

- 需要生成标准Cron表达式
- 需要验证Cron表达式格式是否正确
- 需要计算下次执行时间
- 需要解析Cron表达式为人类可读格式
- 需要列出多个未来执行时间点
- 需要将自然语言转换为Cron表达式

## Out of Scope

- 处理非标准Cron变体（如Quartz、AWS等扩展语法）
- 时区转换（使用系统本地时间）
- 分布式调度系统协调
- 任务依赖管理
- 执行历史记录
- 任务失败重试逻辑

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Python API

```python
from main import CronSkill
from datetime import datetime

skill = CronSkill()

# 验证表达式
is_valid, error = skill.validate('0 9 * * 1-5')

# 获取下次执行时间
next_run = skill.get_next('0 0 * * *', datetime.now())

# 获取多个执行时间
runs = skill.get_next_n('*/5 * * * *', n=5)

# 解析为可读文本
description = skill.describe('0 9 * * 1-5')

# 生成表达式
expression = skill.generate('daily at 9am')

# 列出字段说明
fields = skill.get_field_info()
```

### CLI Usage

```bash
# 验证表达式
python main.py validate "0 9 * * 1-5"

# 获取下次执行时间
python main.py next "0 0 * * *"

# 获取多个执行时间
python main.py schedule "*/30 * * * *" --count 10

# 解析表达式
python main.py describe "0 0 * * 0"

# 生成表达式
python main.py generate "every 5 minutes"

# 列出所有预设
python main.py presets
```

## Cron Format

```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday = 0)
│ │ │ │ │
* * * * *
```

### Special Characters

| Character | Meaning | Example |
|-----------|---------|---------|
| `*` | Any value | `* * * * *` = every minute |
| `,` | List separator | `0,30 * * * *` = :00 and :30 |
| `-` | Range | `9-17 * * * *` = 9AM to 5PM |
| `/` | Step | `*/5 * * * *` = every 5 minutes |

## Preset Expressions

| Preset | Expression | Description |
|--------|------------|-------------|
| `@yearly` | `0 0 1 1 *` | Every year |
| `@monthly` | `0 0 1 * *` | Every month |
| `@weekly` | `0 0 * * 0` | Every week |
| `@daily` | `0 0 * * *` | Every day |
| `@hourly` | `0 * * * *` | Every hour |
| `@reboot` | - | At system start |

## Examples

见 [examples.md](examples.md)

## Testing

```bash
pytest test_main.py -v
```

## License

MIT
