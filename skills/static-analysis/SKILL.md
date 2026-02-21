# Static Analysis - 代码静态分析工具

> 专业的Python代码静态分析工具，支持代码质量检查、复杂度分析、安全检查、风格检查和自动生成报告

---

## 功能概述

本Skill提供企业级的Python代码分析能力，帮助开发者发现代码中的潜在问题、安全漏洞和风格不一致。

## 何时使用本Skill

**Use this skill when:**
- 需要分析Python代码质量
- 检查代码复杂度和可维护性
- 扫描安全漏洞和危险代码模式
- 检查代码风格一致性
- 生成代码质量报告
- 持续集成中的代码检查

**触发关键词：** "static analysis", "code quality", "complexity check", "security scan", "linting", "code review", "代码分析", "代码质量"

**典型场景：**
1. 代码审查前的自我检查
2. 项目质量评估
3. 技术债务识别
4. 安全漏洞扫描
5. CI/CD流水线集成

### 核心能力

1. **代码复杂度分析** - 计算圈复杂度，识别过于复杂的函数
2. **安全漏洞扫描** - 检测危险函数、硬编码密钥、SQL注入等
3. **代码风格检查** - 检查PEP8规范、行长度、缩进等
4. **代码指标统计** - 行数、函数数、类数、可维护性指数
5. **多格式报告** - HTML、JSON、Markdown报告生成

---

## 使用方法

### 基础用法

```bash
# 分析整个项目
kimi skill run static-analysis --params "action=analyze&target=./src"

# 只分析复杂度
kimi skill run static-analysis --params "action=complexity&target=./src"

# 只进行安全扫描
kimi skill run static-analysis --params "action=security&target=./src"

# 只检查代码风格
kimi skill run static-analysis --params "action=style&target=./src"

# 生成配置文件模板
kimi skill run static-analysis --params "action=generate-config"
```

### 高级用法

```bash
# 严格模式分析
kimi skill run static-analysis \
  --params "action=analyze&target=./src&strict_mode=true&min_complexity=5"

# 排除特定目录
kimi skill run static-analysis \
  --params "action=analyze&target=./src&exclude_patterns=tests,examples,__pycache__"

# 生成JSON格式报告
kimi skill run static-analysis \
  --params "action=analyze&target=./src&format=json"

# 与基线对比
kimi skill run static-analysis \
  --params "action=compare&target=./src&baseline_path=./baseline-report.json"
```

---

## 参数说明

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|-------|------|------|-------|------|
| `action` | string | 是 | - | 操作类型: analyze/complexity/security/style/compare/generate-config |
| `target` | string | 是 | - | 分析目标路径（文件或目录） |
| `output_dir` | string | 否 | ./analysis-results | 结果输出目录 |
| `exclude_patterns` | string | 否 | 内置 | 排除模式，逗号分隔 |
| `min_complexity` | integer | 否 | 10 | 最小复杂度阈值 |
| `max_line_length` | integer | 否 | 100 | 最大行长度 |
| `strict_mode` | boolean | 否 | false | 严格模式 |
| `baseline_path` | string | 否 | - | 基线报告路径 |
| `format` | string | 否 | html | 报告格式: html/json/markdown |

---

## 示例

### 示例1：项目质量评估

```bash
kimi skill run static-analysis \
  --params "action=analyze&target=./my-project&output_dir=./quality-report"
```

分析报告包含:
- 项目整体代码统计
- 复杂度高的函数列表
- 安全漏洞警告
- 风格问题汇总
- 可维护性指数

### 示例2：安全检查

```bash
kimi skill run static-analysis \
  --params "action=security&target=./src"
```

检测的安全问题包括:
- 使用eval/exec等危险函数
- 硬编码密码/密钥
- 潜在的SQL注入
- 不安全的反序列化

### 示例3：代码复杂度分析

```bash
kimi skill run static-analysis \
  --params "action=complexity&target=./src&min_complexity=15"
```

复杂度分级:
- **1-10**: 简单，易于维护
- **11-20**: 中等，需要关注
- **21+**: 复杂，需要重构

### 示例4：CI/CD集成

```bash
# 分析并设置严格标准
kimi skill run static-analysis \
  --params "action=analyze&target=./src&strict_mode=true&format=json"

# 检查退出码
# 0 - 无问题
# 1 - 复杂度或风格问题
# 2 - 存在安全问题
```

---

## 报告解读

### HTML报告

可视化报告包含以下部分:

1. **汇总卡片** - 快速查看各项指标
2. **复杂度问题** - 高复杂度函数列表
3. **安全问题** - 按严重程度分类
4. **风格问题** - 代码风格违规
5. **文件指标** - 每个文件的详细统计

### 可维护性指数 (MI)

| 范围 | 评级 | 说明 |
|------|------|------|
| 85-100 | 优秀 | 代码易于维护 |
| 65-84 | 良好 | 可接受的范围 |
| 0-64 | 较差 | 需要重构 |

---

## 最佳实践

### 1. 复杂度控制

```bash
# 设置合理的复杂度阈值
# 推荐: min_complexity=10

kimi skill run static-analysis \
  --params "action=analyze&target=./src&min_complexity=10"
```

### 2. 排除第三方代码

```bash
# 排除不需要分析的文件
kimi skill run static-analysis \
  --params "action=analyze&target=./src&exclude_patterns=venv,node_modules,migrations,tests"
```

### 3. 渐进式改进

```bash
# 先生成基线报告
kimi skill run static-analysis \
  --params "action=analyze&target=./src&format=json&output_dir=./baseline"

# 后续对比改进
kimi skill run static-analysis \
  --params "action=compare&target=./src&baseline_path=./baseline/report.json"
```

---

## CI/CD集成

### GitHub Actions

```yaml
name: Code Quality Check
on: [push, pull_request]
jobs:
  static-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Static Analysis
        run: |
          kimi skill run static-analysis \
            --params "action=analyze&target=./src&format=json"
      
      - name: Check Security Issues
        run: |
          if grep -q '"severity": "critical"' ./analysis-results/*.json; then
            echo "Critical security issues found!"
            exit 1
          fi
      
      - name: Upload Report
        uses: actions/upload-artifact@v4
        with:
          name: analysis-report
          path: ./analysis-results/
```

---

## 技术细节

### 依赖要求

- Python 3.10+
- ast-decompiler 0.7+
- radon 6.0+
- bandit 1.7+

### 分析算法

1. **圈复杂度** - 基于AST分析控制流
2. **可维护性指数** - Halstead指标 + 圈复杂度 + 代码行数
3. **安全扫描** - 模式匹配 + AST遍历
4. **风格检查** - 正则表达式 + 语法分析

### 安全规则

| 规则 | 严重程度 | 说明 |
|------|----------|------|
| eval/exec | 严重 | 危险函数调用 |
| hardcoded_secret | 高 | 硬编码密钥 |
| potential_sql_injection | 高 | SQL注入风险 |
| pickle.loads | 高 | 不安全反序列化 |
| yaml.load | 高 | 不安全YAML加载 |

---

## 故障排除

### 常见问题

**Q: 分析速度慢**
- 使用`exclude_patterns`排除大目录
- 只分析特定文件而非整个项目

**Q: 误报太多**
- 调整`min_complexity`阈值
- 使用`strict_mode=false`

**Q: 缺少某些问题**
- 启用`strict_mode=true`
- 降低`min_complexity`值

---

## API参考

### StaticAnalyzer类

```python
from main import StaticAnalyzer, AnalysisConfig

config = AnalysisConfig(
    target='./src',
    min_complexity=10,
    strict_mode=True
)

analyzer = StaticAnalyzer(config)
report = analyzer.analyze()

print(f"Found {len(report.security_issues)} security issues")
print(f"Found {len(report.complexity_issues)} complexity issues")
```

---

*Version: 1.0.0 | License: MIT | Author: Godlike Kimi Skills*
