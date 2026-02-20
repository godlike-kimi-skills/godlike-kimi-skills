# pytest-skill

PyTest测试框架Skill，提供自动化测试生成、覆盖率分析和Fixtures管理功能。

## Use When

- 需要为Python项目创建或优化测试用例
- 需要生成测试代码或测试模板
- 需要分析测试覆盖率并生成报告
- 需要管理复杂的测试Fixtures和依赖
- 需要配置PyTest项目设置
- 需要运行测试并解析结果
- 需要迁移unittest到pytest
- 需要设置CI/CD测试流水线

## Out of Scope

- 不处理非Python语言的测试
- 不替代手动编写复杂的业务逻辑测试
- 不提供测试数据生成功能（建议使用hypothesis）
- 不处理性能基准测试（建议使用pytest-benchmark）
- 不管理测试环境的基础设施

## Installation

```bash
pip install pytest pytest-cov pytest-xdist pytest-mock
```

## Quick Start

### 生成测试代码

```python
from pytest_skill import PytestSkill

skill = PytestSkill()

# 为模块生成测试
test_code = skill.generate_tests("my_module.py")
print(test_code)
```

### 运行测试并分析

```python
# 运行测试并获取报告
result = skill.run_tests("tests/", coverage=True)
print(f"通过率: {result['pass_rate']}%")
```

### 分析覆盖率

```python
# 生成覆盖率报告
coverage = skill.analyze_coverage("my_package/")
skill.generate_coverage_report(coverage, "html")
```

## Features

### 1. 智能测试生成
- 基于代码结构自动生成测试模板
- 支持类方法和函数测试
- 生成参数化测试用例建议

### 2. 覆盖率分析
- 语句覆盖率分析
- 分支覆盖率检测
- 缺失测试标识
- HTML/XML报告生成

### 3. Fixtures管理
- Fixtures依赖图分析
- 自动Fixtures发现
- Fixtures作用域优化建议
- 冲突检测

### 4. 配置管理
- pytest.ini/pyproject.toml配置
- 并发测试配置
- 插件管理

## API Reference

### PytestSkill

主类，提供所有pytest相关功能。

#### Methods

- `generate_tests(source_path, output_path=None)` - 生成测试代码
- `run_tests(test_path, **options)` - 运行测试
- `analyze_coverage(source_path)` - 分析覆盖率
- `generate_coverage_report(coverage_data, format='html')` - 生成报告
- `analyze_fixtures(test_path)` - 分析Fixtures
- `optimize_fixtures(fixtures_data)` - 优化Fixtures配置
- `configure_project(config_path, settings)` - 配置项目

## Configuration

### pytest.ini 示例

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
```

### pyproject.toml 示例

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short --strict-markers"
```

## Examples

### 示例1: 生成数据类测试

```python
skill = PytestSkill()
code = '''
from dataclasses import dataclass

@dataclass
class User:
    name: str
    email: str
    age: int
'''

test = skill.generate_tests_from_code(code)
# 生成包含边界值测试的完整测试代码
```

### 示例2: 并发测试配置

```python
skill.configure_project("pyproject.toml", {
    "addopts": "-n auto --dist=loadfile",
    "plugins": ["pytest-xdist"]
})
```

### 示例3: Fixtures分析

```python
fixtures = skill.analyze_fixtures("tests/")
print(f"发现 {len(fixtures)} 个fixtures")
for fixture in fixtures:
    print(f"  - {fixture['name']}: {fixture['scope']}")
```

## Best Practices

1. **测试命名**: 使用描述性的测试函数名
2. **Fixtures作用域**: 合理设置scope减少开销
3. **参数化**: 使用@pytest.mark.parametrize减少重复
4. **Mock使用**: 适当使用mock隔离外部依赖
5. **覆盖率目标**: 建议保持80%以上覆盖率

## Troubleshooting

### 常见问题

**Q: 测试发现失败**
A: 检查pytest.ini配置中的testpaths和python_files设置

**Q: Fixtures冲突**
A: 使用analyze_fixtures()检测命名冲突

**Q: 覆盖率不准确**
A: 确保source_path指向正确的源代码目录

## License

MIT License
