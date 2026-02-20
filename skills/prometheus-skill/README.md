# Prometheus Skill

Prometheus监控查询工具，支持PromQL查询、指标分析和告警规则管理。

## Use When
- 查询Prometheus监控指标
- 分析系统性能指标
- 管理告警规则
- 导出监控数据
- 生成指标报告
- 关键词触发：`Prometheus`、`PromQL`、`监控查询`、`metrics query`、`告警规则`、`alert rule`、`指标分析`、`metric analysis`

## Out of Scope
- Prometheus服务器部署
- 数据持久化存储
- 复杂告警通知
- 分布式追踪

## Quick Start

```python
from main import PrometheusClient

# 连接Prometheus
client = PrometheusClient("http://localhost:9090")

# 执行PromQL查询
result = client.query('up{job="prometheus"}')
print(result)

# 查询范围数据
range_data = client.query_range(
    'rate(http_requests_total[5m])',
    start='-1h',
    end='now',
    step='1m'
)
```

## Features

- 🔍 PromQL查询执行
- 📊 指标分析和聚合
- ⚠️ 告警规则管理
- 📈 范围查询支持
- 📤 数据导出功能

## Installation

```bash
pip install -r requirements.txt
```

## License

MIT
