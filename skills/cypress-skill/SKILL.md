# Cypress Skill

Cypress E2E测试智能助手。Use when writing tests, automating testing, or when user mentions 'Cypress', 'E2E testing', 'end-to-end testing', 'browser automation'.

## Capabilities

- **测试生成**: 自动生成Cypress E2E测试代码
- **Page Object**: 创建Page Object模式代码
- **Fixtures**: 管理测试数据和Fixtures
- **自定义命令**: 生成自定义Cypress命令
- **报告生成**: 生成测试报告和分析

## Usage

### 生成E2E测试
```python
from main import CypressSkill

skill = CypressSkill()
test_code = skill.generate_test(
    url="https://example.com/login",
    actions=["fill username", "fill password", "click login"],
    assertions=["url should be /dashboard", "see welcome message"]
)
```

### 创建Page Object
```python
page_object = skill.generate_page_object(
    page_name="LoginPage",
    elements=[
        {"name": "username", "selector": "#username", "type": "input"},
        {"name": "password", "selector": "#password", "type": "input"}
    ]
)
```

### 生成Fixture
```python
fixture = skill.generate_fixture(
    name="users",
    data={"admin": {"username": "admin", "role": "administrator"}}
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
