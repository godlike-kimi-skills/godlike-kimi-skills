# UUID Generator Skill

UUID和标识符生成工具，支持多版本UUID、随机字符串、短ID生成。

## Use When

- 需要生成UUID作为数据库主键
- 需要生成随机标识符用于API密钥
- 需要生成短ID用于URL缩短
- 需要生成特定版本的UUID（v1, v4, v7）
- 需要生成安全随机字符串
- 需要生成可排序的标识符

## Out of Scope

- UUID命名空间管理（DNS、URL等）
- UUID v2、v3、v5生成（较少使用）
- 分布式ID生成协调（如雪花算法集群）
- 密码学安全的密钥生成（使用专用工具）
- ID冲突检测服务
- ID序列化存储管理

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Python API

```python
from main import UUIDGeneratorSkill

skill = UUIDGeneratorSkill()

# 生成UUID v4 (随机)
uuid_v4 = skill.uuid_v4()

# 生成UUID v1 (时间戳+MAC)
uuid_v1 = skill.uuid_v1()

# 生成UUID v7 (时间排序)
uuid_v7 = skill.uuid_v7()

# 生成随机字符串
random_str = skill.random_string(length=32)

# 生成短ID
short_id = skill.short_id(length=8)

# 生成NanoID
nanoid = skill.nanoid(size=21)

# 生成CUID
cuid = skill.cuid()

# 批量生成
uuids = skill.batch_uuid_v4(count=10)

# 验证UUID
is_valid = skill.validate('550e8400-e29b-41d4-a716-446655440000')

# 解析UUID
info = skill.parse('550e8400-e29b-41d4-a716-446655440000')
```

### CLI Usage

```bash
# 生成UUID v4
python main.py uuid

# 生成多个UUID
python main.py uuid --count 5 --version 4

# 生成短ID
python main.py short --length 8

# 生成随机字符串
python main.py random --length 32 --alphanumeric

# 生成NanoID
python main.py nanoid

# 验证UUID
python main.py validate 550e8400-e29b-41d4-a716-446655440000

# 解析UUID
python main.py parse 550e8400-e29b-41d4-a716-446655440000
```

## UUID Versions

| Version | Format | Use Case |
|---------|--------|----------|
| v1 | 时间戳 + MAC地址 | 需要可追踪的时间顺序 |
| v4 | 完全随机 | 通用唯一标识 |
| v7 | 时间戳 + 随机 | 可排序的唯一标识 |

## ID Types

| Type | Length | Characters | Collision Risk |
|------|--------|------------|----------------|
| UUID | 36 | Hex + dashes | Extremely low |
| Short ID | 7-12 | Base62 | Low |
| NanoID | 21 | Base64-like | Very low |
| CUID | 25 | Base36 | Very low |
| Random | Custom | Configurable | Depends on length |

## Examples

见 [examples.md](examples.md)

## Testing

```bash
pytest test_main.py -v
```

## License

MIT
