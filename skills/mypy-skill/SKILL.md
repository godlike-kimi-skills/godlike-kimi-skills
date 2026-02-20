# mypy-skill

Python类型检查Skill，集成mypy提供静态类型分析和错误修复功能。

## Use When

- 需要检查Python代码的类型正确性
- 需要为遗留代码添加类型注解
- 需要修复mypy报告的类型错误
- 需要配置mypy检查规则
- 需要生成类型覆盖率报告
- 需要在CI中集成类型检查
- 需要逐步迁移代码到类型安全
- 需要理解复杂的类型错误信息

## Out of Scope

- 不处理运行时类型检查（这是Python本身的行为）
- 不进行代码逻辑验证（只检查类型）
- 不自动修复所有类型问题（需要人工判断）
- 不处理C扩展的类型检查
- 不替代单元测试和集成测试
- 不处理动态类型特性（如`eval`、`exec`）

## Installation

```bash
pip install mypy types-requests types-setuptools
```

## Quick Start

### 检查单个文件

```python
from mypy_skill import MypySkill

skill = MypySkill()

# 检查代码
result = skill.check_file("my_module.py")
print(f"发现 {len(result['errors'])} 个类型错误")
```

### 修复类型错误

```python
# 自动修复可修复的错误
fixed = skill.fix_errors("my_module.py")
print(f"修复了 {fixed['fixed_count']} 个错误")
```

### 生成类型注解

```python
# 为遗留代码生成类型注解
annotations = skill.generate_annotations("legacy_module.py")
print(annotations)
```

## Features

### 1. 类型检查
- 完整的mypy集成
- 错误分类和过滤
- 增量检查支持
- 缓存管理

### 2. 错误修复
- 自动修复简单类型错误
- 修复建议生成
- 批量修复支持
- 修复历史记录

### 3. 类型注解生成
- 基于推断生成注解
- 函数签名生成
- 类属性注解
- 复杂类型处理

### 4. 配置管理
- mypy.ini/pyproject.toml配置
- 忽略规则管理
- 严格模式配置
- 第三方stub管理

## API Reference

### MypySkill

主类，提供类型检查相关功能。

#### Methods

- `check_file(file_path, **options)` - 检查单个文件
- `check_project(project_path, **options)` - 检查整个项目
- `fix_errors(file_path, **options)` - 修复类型错误
- `generate_annotations(file_path, **options)` - 生成类型注解
- `configure_project(config_path, settings)` - 配置项目
- `analyze_errors(errors)` - 分析错误
- `get_error_stats(project_path)` - 获取错误统计

## Configuration

### mypy.ini 配置

```ini
[mypy]
python_version = 3.10
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
strict_equality = True
show_error_codes = True
show_column_numbers = True

# 忽略某些模块
ignore_missing_imports = True

# 模块特定配置
[mypy.plugins.django.*]
ignore_missing_imports = True

[mypy-tests.*]
disallow_untyped_defs = False
```

### pyproject.toml 配置

```toml
[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
show_error_codes = true
show_column_numbers = true
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

### 配置选项说明

| 选项 | 说明 | 建议 |
|------|------|------|
| `disallow_untyped_defs` | 要求所有函数有类型注解 | 新项目启用 |
| `ignore_missing_imports` | 忽略缺失的导入 | 迁移期启用 |
| `warn_return_any` | 返回Any时警告 | 总是启用 |
| `strict_equality` | 严格相等检查 | 总是启用 |

## Examples

### 示例1: 渐进式类型检查

```python
skill = MypySkill()

# 先检查核心模块
result = skill.check_file("core/module.py")

if result['errors']:
    # 分析错误
    analysis = skill.analyze_errors(result['errors'])
    print(f"最严重的问题: {analysis['most_common']}")
    
    # 修复能自动修复的
    fixed = skill.fix_errors("core/module.py")
    print(f"自动修复了 {fixed['fixed_count']} 个问题")
```

### 示例2: 生成类型注解

```python
skill = MypySkill()

# 为遗留代码生成注解
code = '''
def process_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result
'''

annotations = skill.generate_annotations_from_code(code)
# 返回带注解的代码
```

### 示例3: CI集成

```python
# CI脚本
skill = MypySkill()
result = skill.check_project("src/", strict=True)

if result['error_count'] > 0:
    print("类型检查失败!")
    for error in result['errors'][:10]:  # 显示前10个
        print(f"  {error['file']}:{error['line']}: {error['message']}")
    exit(1)
```

### 示例4: 错误统计

```python
skill = MypySkill()
stats = skill.get_error_stats("src/")

print(f"总错误数: {stats['total']}")
print("错误分类:")
for category, count in stats['by_category'].items():
    print(f"  {category}: {count}")
```

## Best Practices

1. **渐进式采用**: 从关键模块开始，逐步扩展
2. **配置管理**: 使用pyproject.toml集中配置
3. **CI集成**: 在CI中运行类型检查
4. **类型stub**: 为第三方库使用stub文件
5. **文档**: 为公共API添加类型文档

## Troubleshooting

### 常见问题

**Q: mypy报告大量第三方库错误**
A: 启用 `ignore_missing_imports = True` 或安装对应的types包

**Q: 动态类型代码报错**
A: 使用 `typing.Any` 或 `# type: ignore` 注释

**Q: 循环导入导致类型错误**
A: 使用 `if TYPE_CHECKING:` 块延迟导入

**Q: 装饰器导致类型丢失**
A: 使用 `typing.ParamSpec` 或第三方装饰器类型stub

## License

MIT License
