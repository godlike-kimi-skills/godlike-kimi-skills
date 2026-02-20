# JSON/YAML Skill

JSON与YAML格式处理工具，支持格式转换、验证、查询和美化。

## Use When

- 需要在JSON和YAML格式之间转换配置文件
- 需要验证JSON/YAML文件格式是否正确
- 需要从JSON/YAML文件中提取特定数据
- 需要美化或压缩JSON/YAML输出
- 需要合并多个JSON/YAML文件
- 需要比较两个JSON/YAML文件的差异

## Out of Scope

- 处理超过100MB的大型文件（性能限制）
- 支持JSON5、HJSON等非标准JSON格式
- XML格式处理
- 数据加密/解密操作
- 数据库连接和查询
- HTTP API请求处理

## Installation

```bash
# 安装依赖
pip install -r requirements.txt
```

## Usage

### Python API

```python
from main import JsonYamlSkill

skill = JsonYamlSkill()

# JSON转YAML
yaml_str = skill.json_to_yaml('{"name": "test", "value": 123}')

# YAML转JSON
json_str = skill.yaml_to_json("name: test\nvalue: 123")

# 验证JSON
is_valid, error = skill.validate_json('{"key": "value"}')

# 查询数据
result = skill.query_json('{"users": [{"name": "Alice"}]}', '$.users[0].name')

# 美化JSON
pretty = skill.beautify_json('{"a":1}', indent=4)
```

### CLI Usage

```bash
# 格式转换
python main.py convert input.json output.yaml

# 验证文件
python main.py validate data.json

# 查询数据
python main.py query data.json '$.users[*].name'

# 美化文件
python main.py beautify data.json --indent 4
```

## Supported Operations

| Operation | JSON | YAML | Description |
|-----------|------|------|-------------|
| Parse | ✅ | ✅ | 解析字符串为数据结构 |
| Validate | ✅ | ✅ | 验证格式正确性 |
| Convert | ✅ | ✅ | 相互转换 |
| Query | ✅ | ✅ | JSONPath查询 |
| Beautify | ✅ | ✅ | 格式化美化 |
| Minify | ✅ | ✅ | 压缩输出 |
| Merge | ✅ | ✅ | 合并多个文件 |
| Diff | ✅ | ✅ | 比较差异 |

## JSONPath Support

支持标准JSONPath表达式：
- `$` - 根元素
- `$.key` - 访问对象属性
- `$[0]` - 数组索引
- `$[*]` - 所有数组元素
- `$..key` - 递归查找
- `$.key[?(@.value > 10)]` - 过滤表达式

## Examples

见 [examples.md](examples.md)

## Testing

```bash
pytest test_main.py -v
```

## License

MIT
