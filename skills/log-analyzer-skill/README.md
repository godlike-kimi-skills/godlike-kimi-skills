# Log Analyzer Skill

智能日志分析工具，支持Nginx、Apache、应用程序日志的解析、错误统计和趋势分析。

## Use When
- 分析服务器日志（Nginx、Apache、系统日志）
- 识别错误模式和异常趋势
- 生成日志分析报告
- 监控应用程序日志
- 排查生产环境问题
- 关键词触发：`日志分析`、`log analysis`、`错误统计`、`error analysis`、`Nginx日志`、`Apache日志`、`趋势分析`

## Out of Scope
- 实时监控告警（使用 alert-manager）
- 日志收集和存储（使用 log-manager）
- 分布式追踪分析
- 安全入侵检测

## Quick Start

```python
from main import LogAnalyzer

# 初始化分析器
analyzer = LogAnalyzer()

# 分析Nginx日志
result = analyzer.analyze_nginx_log("/var/log/nginx/access.log")
print(result.summary())

# 分析错误趋势
trend = analyzer.analyze_error_trend("/var/log/app.log", hours=24)
```

## Features

- 🔍 多格式日志解析（Nginx、Apache、自定义格式）
- 📊 错误统计和分类
- 📈 趋势分析和可视化
- ⚡ 高性能流式处理
- 🔧 可自定义解析规则

## Installation

```bash
pip install -r requirements.txt
```

## License

MIT
