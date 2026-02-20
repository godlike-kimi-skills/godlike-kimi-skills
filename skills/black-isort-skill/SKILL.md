# black-isort-skill

Python代码格式化Skill，集成Black和isort提供统一的代码格式化解决方案。

## Use When

- 需要格式化Python代码以符合PEP 8规范
- 需要自动排序和分组import语句
- 需要检查和修复代码风格问题
- 需要在CI/CD中集成代码格式化检查
- 需要配置Black或isort的格式化规则
- 需要批量格式化整个项目
- 需要检查代码是否符合项目规范
- 需要生成格式化差异报告

## Out of Scope

- 不处理非Python语言（如JavaScript、Go等）
- 不进行代码逻辑重构或优化
- 不处理文档字符串内容格式化（仅格式布局）
- 不提供代码风格争议解决（遵循Black的"不可配置"理念）
- 不替代代码审查和人工判断
- 不处理类型注解的语义检查（这是mypy的工作）

## Installation

```bash
pip install black isort
```

## Quick Start

### 格式化单个文件

```python
from black_isort_skill import BlackIsortSkill

skill = BlackIsortSkill()

# 格式化代码
formatted = skill.format_code("import os\nimport sys\n\ndef foo( x,y ):\n  pass")
print(formatted)
```

### 批量格式化项目

```python
# 格式化整个目录
results = skill.format_project("src/", check_only=False)
print(f"格式化完成: {results['formatted']} 个文件")
```

### 检查代码规范

```python
# 检查而不修改
issues = skill.check_format("src/")
print(f"发现问题: {len(issues)} 个文件需要格式化")
```

## Features

### 1. Black代码格式化
- 自动PEP 8格式化
- 行长度控制
- 字符串引号统一
- 尾随逗号处理

### 2. isort导入排序
- 标准库/第三方/本地导入分组
- 按字母顺序排序
- 配置排序规则
- 处理from imports

### 3. 项目配置管理
- pyproject.toml支持
- 独立的Black/isort配置
- 配置文件验证

### 4. 批量处理
- 递归目录处理
- 多进程并行
- 差异报告生成
- Git集成

## API Reference

### BlackIsortSkill

主类，提供代码格式化功能。

#### Methods

- `format_code(code, **options)` - 格式化代码字符串
- `format_file(file_path, **options)` - 格式化单个文件
- `format_project(project_path, **options)` - 批量格式化项目
- `check_format(path)` - 检查格式，不修改
- `configure_project(config_path, settings)` - 配置项目
- `generate_diff(original, formatted)` - 生成差异
- `is_formatted(file_path)` - 检查文件是否已格式化

## Configuration

### pyproject.toml 配置

```toml
[tool.black]
line-length = 88
target-version = ['py38', 'py39', 'py310']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
line_length = 88
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
src_paths = ["src", "tests"]
known_first_party = ["my_package"]
known_third_party = ["django", "requests"]
```

### 常用配置选项

| 选项 | Black | isort | 说明 |
|------|-------|-------|------|
| line-length | ✓ | ✓ | 行长度限制 |
| target-version | ✓ | - | Python版本目标 |
| skip-string-normalization | ✓ | - | 跳过引号规范化 |
| profile | - | ✓ | 配置预设 |
| force_single_line | - | ✓ | 强制单行导入 |
| order_by_type | - | ✓ | 按类型排序 |

## Examples

### 示例1: 格式化前检查

```python
skill = BlackIsortSkill()

# 先检查
issues = skill.check_format("src/")
if issues:
    print(f"发现 {len(issues)} 个文件需要格式化:")
    for issue in issues:
        print(f"  - {issue['file']}")
    
    # 询问是否格式化
    skill.format_project("src/")
```

### 示例2: 自定义配置

```python
skill = BlackIsortSkill()

# 配置项目
skill.configure_project("pyproject.toml", {
    "black": {
        "line-length": 100,
        "target-version": ["py39"]
    },
    "isort": {
        "profile": "black",
        "known_first_party": ["myapp"]
    }
})
```

### 示例3: Git集成

```python
# 只格式化修改的文件
changed_files = skill.get_git_changed_files()
for file in changed_files:
    if file.endswith('.py'):
        skill.format_file(file)
```

### 示例4: CI检查

```python
# CI模式下只检查，不修改
skill = BlackIsortSkill()
result = skill.format_project("src/", check_only=True)

if result['needs_formatting']:
    print("代码格式不符合规范!")
    for file in result['unformatted']:
        print(f"  - {file}")
    exit(1)
```

## Best Practices

1. **预提交钩子**: 配置pre-commit自动格式化
2. **CI集成**: 在CI中运行格式检查
3. **编辑器集成**: 配置编辑器保存时自动格式化
4. **团队规范**: 统一配置，避免格式战争
5. **渐进式采用**: 对新代码强制格式化，旧代码逐步迁移

## Troubleshooting

### 常见问题

**Q: Black和isort配置冲突**
A: 确保isort配置 `profile = "black"`，让isort兼容Black格式

**Q: 某些文件不想格式化**
A: 在配置中添加 `extend-exclude` 或 `skip` 配置

**Q: 格式化后import顺序不对**
A: 检查 `known_first_party` 和 `known_third_party` 配置

**Q: CI检查失败但本地正常**
A: 确保Black和isort版本一致

## License

MIT License
