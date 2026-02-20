# Log Analyzer Skill

## Description

智能日志分析工具，支持Nginx、Apache、应用程序日志的解析、错误统计和趋势分析。关键词触发：`日志分析`、`log analysis`、`error analysis`、`Nginx日志`、`Apache日志`、`日志解析`、`log parsing`、`错误模式`、`error pattern`、`日志趋势`、`log trend`。

## Use When

- 需要分析服务器访问日志（Nginx、Apache）
- 排查应用程序错误和异常
- 生成日志分析报告和统计
- 识别错误模式和异常趋势
- 分析用户访问行为和流量模式
- 监控系统日志和性能指标
- 故障排查和根因分析

## Out of Scope

- 实时监控和告警通知（使用 alert-manager skill）
- 日志的集中收集和存储管理（使用 log-manager skill）
- 分布式链路追踪分析
- 安全入侵检测和审计
- 日志的实时流处理
- 机器学习异常检测

## Usage

### Basic Usage

```python
from main import LogAnalyzer

# 创建分析器实例
analyzer = LogAnalyzer()

# 分析Nginx访问日志
nginx_stats = analyzer.analyze_nginx_log("/var/log/nginx/access.log")
print(f"总请求数: {nginx_stats['total_requests']}")
print(f"错误率: {nginx_stats['error_rate']:.2%}")

# 分析Apache日志
apache_stats = analyzer.analyze_apache_log("/var/log/apache2/access.log")
print(f"独立IP数: {apache_stats['unique_ips']}")
```

### Advanced Usage

```python
# 分析错误趋势
trend = analyzer.analyze_error_trend(
    log_path="/var/log/app.log",
    hours=24,
    error_patterns=[r"ERROR", r"EXCEPTION", r"FATAL"]
)

# 生成完整分析报告
report = analyzer.generate_report(
    log_files=["/var/log/nginx/access.log", "/var/log/app.log"],
    output_format="json"
)

# 自定义日志格式解析
custom_parser = analyzer.create_parser(
    format_pattern=r'^(?P<timestamp>\S+) (?P<level>\w+) (?P<message>.*)$'
)
results = custom_parser.parse("/var/log/custom.log")
```

### Command Line Usage

```bash
# 分析单个日志文件
python main.py --input /var/log/nginx/access.log --format nginx --output report.json

# 分析错误趋势
python main.py --input /var/log/app.log --analyze-trend --hours 24

# 生成HTML报告
python main.py --input /var/log/apache2/access.log --format apache --output report.html --report-type html
```

## API Reference

### LogAnalyzer Class

#### `analyze_nginx_log(log_path, **options)`
分析Nginx访问日志
- **参数**: `log_path` (str) - 日志文件路径
- **返回**: dict - 包含请求统计、错误率、热门URL等

#### `analyze_apache_log(log_path, **options)`
分析Apache访问日志
- **参数**: `log_path` (str) - 日志文件路径
- **返回**: dict - 包含访问统计、响应时间、状态码分布等

#### `analyze_error_trend(log_path, hours=24, error_patterns=None)`
分析错误趋势
- **参数**: 
  - `log_path` (str) - 日志文件路径
  - `hours` (int) - 分析时间范围（小时）
  - `error_patterns` (list) - 错误匹配模式列表
- **返回**: dict - 时间序列错误数据

#### `generate_report(log_files, output_format='json')`
生成综合分析报告
- **参数**: 
  - `log_files` (list) - 日志文件路径列表
  - `output_format` (str) - 输出格式 (json/html/markdown)
- **返回**: str - 报告内容或文件路径

## Configuration

### 支持的日志格式

| 格式 | 描述 | 自动检测 |
|------|------|----------|
| nginx | Nginx combined格式 | ✅ |
| nginx_json | Nginx JSON格式 | ✅ |
| apache | Apache combined格式 | ✅ |
| apache_common | Apache common格式 | ✅ |
| syslog | 系统日志格式 | ✅ |
| json | JSON格式日志 | ✅ |
| custom | 自定义格式 | 需配置 |

### 环境变量

```bash
LOG_ANALYZER_MAX_LINES=1000000  # 最大处理行数
LOG_ANALYZER_CHUNK_SIZE=10000   # 分块读取大小
LOG_ANALYZER_TIMEZONE=UTC       # 默认时区
```

## Examples

### 示例1：网站流量分析

```python
analyzer = LogAnalyzer()
stats = analyzer.analyze_nginx_log("access.log")

print(f"总访问量: {stats['total_requests']}")
print(f"独立访客: {stats['unique_visitors']}")
print(f"平均响应时间: {stats['avg_response_time']}ms")
print(f"错误请求: {stats['error_requests']}")

# 热门页面
for url, count in stats['top_urls'][:10]:
    print(f"  {url}: {count}次访问")
```

### 示例2：错误日志聚合分析

```python
# 分析多个错误日志
error_logs = [
    "/var/log/app/error.log",
    "/var/log/app/exception.log",
    "/var/log/nginx/error.log"
]

for log_file in error_logs:
    errors = analyzer.extract_errors(log_file)
    print(f"\n{log_file}:")
    for error_type, count in errors['by_type'].items():
        print(f"  {error_type}: {count}次")
```

### 示例3：生成监控报告

```python
report = analyzer.generate_report(
    log_files=["access.log", "error.log"],
    output_format="html",
    include_charts=True,
    time_range="last_7_days"
)

with open("log_report.html", "w") as f:
    f.write(report)
```

## Troubleshooting

### 常见问题

1. **大文件处理慢**
   - 使用 `--chunk-size` 参数调整分块大小
   - 启用 `--parallel` 并行处理

2. **编码问题**
   - 指定 `--encoding utf-8` 或 `--encoding gbk`

3. **时间解析错误**
   - 使用 `--timezone` 指定时区
   - 自定义时间格式 `--time-format`

## Related Skills

- `log-manager` - 日志收集和存储管理
- `alert-manager` - 监控告警管理
- `error-tracking-skill` - 错误追踪分析
