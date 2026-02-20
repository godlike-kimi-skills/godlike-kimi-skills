# Load Testing Skill

负载测试工具智能助手。Use when writing tests, automating testing, or when user mentions 'load testing', 'stress testing', 'performance testing', 'Locust', 'k6', 'JMeter'.

## Capabilities

- **Locust脚本生成**: 生成Python Locust负载测试脚本
- **k6脚本生成**: 生成JavaScript k6负载测试脚本
- **测试场景设计**: 设计负载测试场景和策略
- **报告分析**: 分析性能测试结果
- **阈值配置**: 配置性能指标阈值
- **分布式测试**: 生成分布式测试配置

## Usage

### 生成Locust脚本
```python
from main import LoadTestingSkill

skill = LoadTestingSkill()
locust_script = skill.generate_locust_script(
    host="https://api.example.com",
    endpoints=[
        {"path": "/users", "method": "GET", "weight": 3},
        {"path": "/users", "method": "POST", "weight": 1}
    ]
)
```

### 生成k6脚本
```python
k6_script = skill.generate_k6_script(
    url="https://api.example.com",
    scenarios={
        "smoke": {"vus": 10, "duration": "1m"},
        "load": {"vus": 100, "duration": "5m"}
    }
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
