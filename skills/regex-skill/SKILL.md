# Regex Skill

正则表达式工具，支持模式匹配、替换、测试和生成。

## Use When

- 需要从文本中提取特定模式的数据
- 需要验证字符串格式（邮箱、手机号、URL等）
- 需要批量替换或删除文本中的特定模式
- 需要测试正则表达式是否按预期工作
- 需要为常见模式生成正则表达式
- 需要分析和理解复杂的正则表达式

## Out of Scope

- 处理超过10MB的超大文件（内存限制）
- 支持非标准正则语法（如PCRE的所有特性）
- 正则表达式性能优化分析
- 自然语言处理和语义分析
- 加密/解密文本处理
- 二进制数据模式匹配

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Python API

```python
from main import RegexSkill

skill = RegexSkill()

# 匹配模式
matches = skill.match(r'\d+', 'Price: $100')

# 验证格式
is_valid = skill.validate(r'^[\w.-]+@[\w.-]+\.\w+$', 'user@example.com')

# 替换文本
result = skill.replace(r'\d+', 'XXX', 'ID: 12345')

# 测试正则
test_result = skill.test(r'\b\w+@\w+\.\w+\b', ['a@b.c', 'invalid'])

# 生成正则
pattern = skill.generate('email')

# 解释正则
explanation = skill.explain(r'^(?=.*[A-Z])(?=.*\d).{8,}$')
```

### CLI Usage

```bash
# 匹配文本
python main.py match "\d+" "Price: $100"

# 验证格式
python main.py validate "^\w+@\w+\.\w+$" "user@example.com"

# 替换文本
python main.py replace "\s+" "_" "Hello   World"

# 测试正则
python main.py test "\d{3}-\d{4}" --file tests.txt

# 生成正则
python main.py generate email

# 解释正则
python main.py explain "^[a-zA-Z0-9]+$"
```

## Built-in Patterns

| Pattern | Regex | Description |
|---------|-------|-------------|
| email | `[\w.-]+@[\w.-]+\.\w+` | Email address |
| url | `https?://[^\s]+` | HTTP/HTTPS URL |
| ip | `\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}` | IPv4 address |
| phone | `\+?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}` | Phone number |
| date | `\d{4}-\d{2}-\d{2}` | Date (YYYY-MM-DD) |
| uuid | `[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}` | UUID |
| credit_card | `\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}` | Credit card |

## Supported Operations

| Operation | Description |
|-----------|-------------|
| match | 查找所有匹配项 |
| search | 搜索第一个匹配 |
| validate | 验证整个字符串 |
| replace | 替换匹配项 |
| split | 按模式分割 |
| test | 批量测试正则 |
| generate | 生成常见模式 |
| explain | 解释正则含义 |

## Examples

见 [examples.md](examples.md)

## Testing

```bash
pytest test_main.py -v
```

## License

MIT
