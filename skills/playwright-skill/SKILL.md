# Playwright Skill

Playwright自动化测试智能助手。Use when writing tests, automating testing, or when user mentions 'Playwright', 'browser automation', 'multi-browser testing', 'visual regression testing'.

## Capabilities

- **测试生成**: 自动生成Playwright测试代码
- **多浏览器支持**: Chromium、Firefox、WebKit
- **截图对比**: 视觉回归测试
- **测试录制**: 代码生成器支持
- **API测试**: 网络拦截和API测试
- **移动仿真**: 移动设备模拟

## Usage

### 生成测试
```python
from main import PlaywrightSkill

skill = PlaywrightSkill()
test_code = skill.generate_test(
    name="Login Test",
    url="https://example.com",
    steps=[
        {"action": "fill", "selector": "#username", "value": "admin"},
        {"action": "click", "selector": "#login"}
    ]
)
```

### 生成配置
```python
config = skill.generate_config(
    browsers=["chromium", "firefox", "webkit"],
    devices=["iPhone 14", "Pixel 5"]
)
```

### 截图对比
```python
screenshot_code = skill.generate_screenshot_test(
    url="https://example.com",
    selector=".hero-section",
    threshold=0.2
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
