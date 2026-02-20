# Jest Skill

Jest测试框架智能助手。Use when writing tests, automating testing, or when user mentions 'Jest', 'unit testing', 'test coverage', 'mock testing', 'snapshot testing'.

## Capabilities

- **测试生成**: 自动生成Jest单元测试代码
- **Mock创建**: 创建mock函数和模块模拟
- **覆盖率分析**: 分析测试覆盖率并生成报告
- **Snapshot测试**: 创建和管理快照测试
- **测试优化**: 优化现有测试代码

## Usage

### 生成单元测试
```python
from main import JestSkill

skill = JestSkill()
test_code = skill.generate_test(
    source_code="function add(a, b) { return a + b; }",
    test_type="unit"
)
```

### 创建Mock
```python
mock_code = skill.generate_mock(
    module_name="axios",
    methods=["get", "post"]
)
```

### 分析覆盖率
```python
coverage_report = skill.analyze_coverage(
    test_files=["*.test.js"],
    source_files=["src/**/*.js"]
)
```

## Examples

查看 `examples/` 目录获取更多使用示例。

## Testing

运行测试：
```bash
python test_skill.py
```

## License

MIT
