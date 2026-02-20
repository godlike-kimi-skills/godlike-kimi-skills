# Prometheus Skill

## Description

Prometheus监控查询工具，支持PromQL查询、指标分析和告警规则管理。关键词触发：`Prometheus`、`PromQL`、`监控查询`、`metrics query`、`告警规则`、`alert rule`、`指标分析`、`metric analysis`、`时序数据`、`time series`、`监控指标`、`monitoring metrics`。

## Use When

- 需要查询Prometheus监控指标数据
- 执行PromQL查询分析系统状态
- 管理和验证告警规则
- 导出监控数据用于报告
- 分析服务可用性和性能指标
- 查询容器和Kubernetes指标
- 生成监控数据报表

## Out of Scope

- Prometheus服务器的部署和配置
- 长期数据存储和归档（使用专门的存储方案）
- 复杂的告警通知渠道管理（使用 alert-manager）
- 分布式链路追踪分析（使用 Jaeger/Zipkin）
- 日志聚合分析（使用 Loki/ELK）
- 自定义exporter开发

## Usage

### Basic Usage

```python
from main import PrometheusClient

# 创建客户端
client = PrometheusClient("http://localhost:9090")

# 简单查询
result = client.query('up')
print(f"服务状态: {result}")

# 带标签的查询
result = client.query('node_cpu_seconds_total{mode="idle"}')

# 检查服务健康状态
health = client.health_check()
print(f"Prometheus状态: {health['status']}")
```

### Advanced Usage

```python
# 范围查询
range_data = client.query_range(
    query='rate(http_requests_total[5m])',
    start='-1h',
    end='now',
    step='1m'
)

# 获取标签值
labels = client.label_values('job')
print(f"监控任务: {labels}")

# 元数据查询
metadata = client.targets()
for target in metadata['activeTargets']:
    print(f"{target['labels']['job']}: {target['health']}")

# 告警规则管理
rules = client.alert_rules()
for group in rules['groups']:
    print(f"规则组: {group['name']}")
    for rule in group['rules']:
        print(f"  - {rule['name']}: {rule['state']}")
```

### Command Line Usage

```bash
# 执行查询
python main.py --url http://localhost:9090 query "up{job='prometheus'}"

# 范围查询
python main.py --url http://localhost:9090 range "rate(cpu_usage[5m])" --start "-1h" --step "1m"

# 导出指标
python main.py --url http://localhost:9090 export "node_memory_*" --output metrics.json

# 列出告警规则
python main.py --url http://localhost:9090 alerts

# 检查目标状态
python main.py --url http://localhost:9090 targets
```

## API Reference

### PrometheusClient Class

#### `__init__(base_url, timeout=30, headers=None)`
初始化Prometheus客户端
- **参数**: 
  - `base_url` (str) - Prometheus服务器URL
  - `timeout` (int) - 请求超时时间（秒）
  - `headers` (dict) - 自定义请求头

#### `query(query, time=None)`
执行即时查询
- **参数**: 
  - `query` (str) - PromQL查询语句
  - `time` (str) - 查询时间点（可选）
- **返回**: dict - 查询结果

#### `query_range(query, start, end, step)`
执行范围查询
- **参数**: 
  - `query` (str) - PromQL查询语句
  - `start` (str) - 开始时间
  - `end` (str) - 结束时间
  - `step` (str) - 步长间隔
- **返回**: dict - 时序数据

#### `series(match, start=None, end=None)`
查询时间序列元数据
- **参数**: 
  - `match` (list) - 标签匹配器列表
  - `start` (str) - 开始时间（可选）
  - `end` (str) - 结束时间（可选）
- **返回**: list - 时间序列列表

#### `labels(start=None, end=None)`
获取所有标签名称
- **返回**: list - 标签名称列表

#### `label_values(label, match=None)`
获取标签的所有值
- **参数**: 
  - `label` (str) - 标签名称
  - `match` (list) - 标签匹配器（可选）
- **返回**: list - 标签值列表

#### `targets()`
获取监控目标状态
- **返回**: dict - 目标列表和状态

#### `alert_rules()`
获取所有告警规则
- **返回**: dict - 告警规则组

#### `active_alerts()`
获取当前活动告警
- **返回**: list - 活动告警列表

#### `export_metrics(query, format='json', output=None)`
导出指标数据
- **参数**: 
  - `query` (str) - 查询语句
  - `format` (str) - 导出格式（json/csv/prometheus）
  - `output` (str) - 输出文件路径（可选）
- **返回**: str - 导出的数据或文件路径

## Configuration

### 环境变量

```bash
PROMETHEUS_URL=http://localhost:9090  # 默认Prometheus地址
PROMETHEUS_TIMEOUT=30                 # 请求超时时间
PROMETHEUS_USER=admin                 # 认证用户名（可选）
PROMETHEUS_PASSWORD=secret            # 认证密码（可选）
```

### 认证配置

```python
# 基本认证
client = PrometheusClient(
    "http://localhost:9090",
    headers={"Authorization": "Basic dXNlcjpwYXNz"}
)

# Bearer Token认证
client = PrometheusClient(
    "http://localhost:9090",
    headers={"Authorization": "Bearer <token>"}
)
```

## Examples

### 示例1：监控CPU使用率

```python
client = PrometheusClient("http://prometheus:9090")

# 计算CPU使用率
cpu_query = '''
100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
'''

result = client.query(cpu_query)
for series in result['data']['result']:
    instance = series['metric']['instance']
    usage = float(series['value'][1])
    print(f"{instance}: CPU使用率 {usage:.2f}%")
```

### 示例2：监控内存使用

```python
# 内存使用率查询
memory_query = '''
100 * (1 - (
  node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes
))
'''

result = client.query(memory_query)
for series in result['data']['result']:
    instance = series['metric']['instance']
    usage = float(series['value'][1])
    status = "⚠️ 警告" if usage > 80 else "✅ 正常"
    print(f"{instance}: 内存使用率 {usage:.2f}% {status}")
```

### 示例3：HTTP请求速率分析

```python
# 计算每秒HTTP请求数
rate_query = '''
sum by(handler) (rate(http_requests_total[5m]))
'''

range_data = client.query_range(
    query=rate_query,
    start='-1h',
    end='now',
    step='1m'
)

# 分析峰值
for series in range_data['data']['result']:
    handler = series['metric'].get('handler', 'unknown')
    values = [float(v[1]) for v in series['values']]
    avg_rate = sum(values) / len(values)
    max_rate = max(values)
    print(f"{handler}: 平均 {avg_rate:.2f}/s, 峰值 {max_rate:.2f}/s")
```

### 示例4：告警规则验证

```python
# 获取所有告警规则
rules = client.alert_rules()

for group in rules['groups']:
    print(f"\n规则组: {group['name']} (间隔: {group['interval']})")
    for rule in group['rules']:
        state_emoji = {
            'firing': '🔥',
            'pending': '⏳',
            'inactive': '✅'
        }.get(rule['state'], '❓')
        
        print(f"  {state_emoji} {rule['name']}: {rule['state']}")
        if rule['state'] == 'firing':
            print(f"      告警: {rule.get('annotations', {}).get('summary', 'N/A')}")
```

### 示例5：导出监控报告

```python
# 导出关键指标报告
queries = {
    'cpu_usage': '100 - avg(irate(node_cpu_seconds_total{mode="idle"}[5m])) by (instance) * 100',
    'memory_usage': '100 * (1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)',
    'disk_usage': '100 - ((node_filesystem_avail_bytes * 100) / node_filesystem_size_bytes)'
}

report_data = {}
for name, query in queries.items():
    result = client.query(query)
    report_data[name] = result

# 导出为JSON
with open('monitoring_report.json', 'w') as f:
    json.dump(report_data, f, indent=2)
```

## Troubleshooting

### 常见问题

1. **连接超时**
   - 检查Prometheus服务器是否可访问
   - 增加 `--timeout` 参数

2. **查询返回空结果**
   - 验证PromQL语法
   - 检查时间范围是否正确
   - 确认指标名称存在

3. **认证失败**
   - 确认认证信息正确
   - 检查Authorization头格式

## Related Skills

- `grafana-skill` - Grafana仪表板管理
- `alert-manager` - 告警通知管理
- `log-analyzer-skill` - 日志分析
