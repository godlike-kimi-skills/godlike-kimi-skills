# Systematic Debugging

[English](#english) | [中文](#chinese)

---

<a name="english"></a>
## English

### Overview

Systematic Debugging is a structured methodology framework for bug localization and fixing. It helps developers adopt scientific, systematic approaches to diagnose and resolve software issues.

### Features

- **Error Analysis**: Intelligent parsing of error messages and stack traces
- **Debug Strategy**: Recommend the most suitable debugging method
- **Root Cause Analysis**: Locate problem roots using scientific methods
- **Fix Suggestions**: Generate repair solutions based on best practices
- **Multi-language Support**: Python, JavaScript, Java, C/C++, Go, Rust, and more

### Installation

```bash
# Clone the repository
git clone https://github.com/godlike-kimi-skills/systematic-debugging.git

# Navigate to directory
cd systematic-debugging

# Install dependencies (optional)
pip install -r requirements.txt
```

### Usage

#### Command Line

```bash
python main.py --action full_diagnosis --language python --error "ZeroDivisionError"
```

#### As Kimi Skill

```
@systematic-debugging
language: python
error: ValueError: invalid literal
context: x = int(input_str)
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | string | Yes | Operation type: analyze/strategy/root_cause/suggest_fix/full_diagnosis |
| `language` | string | Yes | Programming language |
| `error` | string | No | Error message |
| `context` | string | No | Code context |
| `stack_trace` | string | No | Stack trace |
| `output_format` | string | No | Output format: text/json/markdown |

### Action Types

- **analyze**: Error type and severity analysis
- **strategy**: Recommend debugging approach
- **root_cause**: Deep root cause analysis
- **suggest_fix**: Generate fix suggestions
- **full_diagnosis**: Complete debugging workflow

### Debugging Strategies

| Strategy | Best For |
|----------|----------|
| binary_search | Large codebase, unknown problem location |
| forward | Tracing from input step by step |
| backward | Reverse tracing from error position |
| deductive | Deductive reasoning based on hypotheses |
| inductive | Inducing patterns from observations |
| divide_conquer | Complex systems, modular handling |

### Example Output

```markdown
## Debug Analysis Report

### Error Classification
- **Type**: TypeError
- **Severity**: Medium
- **Language**: Python

### Probable Causes
1. Variable is None (85% probability)
2. Wrong data type passed (10% probability)
3. API response changed (5% probability)

### Recommended Strategy
Binary Search - Isolate problematic code section

### Fix Suggestion
```python
# Add null check
if data is not None:
    result = data.process()
else:
    result = default_value
```
```

### License

MIT License - See [LICENSE](LICENSE)

---

<a name="chinese"></a>
## 中文

### 概述

系统化调试是一个结构化的bug定位和修复方法论框架，帮助开发者采用科学、系统的方式来诊断和解决软件问题。

### 功能特性

- **错误分析**：智能解析错误信息和堆栈跟踪
- **调试策略**：推荐最适合当前问题的调试方法
- **根因分析**：运用科学方法定位问题根源
- **修复建议**：基于最佳实践生成修复方案
- **多语言支持**：Python、JavaScript、Java、C/C++、Go、Rust 等

### 安装

```bash
# 克隆仓库
git clone https://github.com/godlike-kimi-skills/systematic-debugging.git

# 进入目录
cd systematic-debugging

# 安装依赖（可选）
pip install -r requirements.txt
```

### 使用方法

#### 命令行

```bash
python main.py --action full_diagnosis --language python --error "ZeroDivisionError"
```

#### 作为 Kimi Skill

```
@systematic-debugging
语言: python
错误: ValueError: invalid literal
上下文: x = int(input_str)
```

### 参数说明

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `action` | string | 是 | 操作类型：analyze/strategy/root_cause/suggest_fix/full_diagnosis |
| `language` | string | 是 | 编程语言 |
| `error` | string | 否 | 错误信息 |
| `context` | string | 否 | 代码上下文 |
| `stack_trace` | string | 否 | 堆栈跟踪 |
| `output_format` | string | 否 | 输出格式：text/json/markdown |

### 操作类型

- **analyze**：错误类型和严重程度分析
- **strategy**：推荐调试方法
- **root_cause**：深度根因分析
- **suggest_fix**：生成修复建议
- **full_diagnosis**：完整调试流程

### 调试策略

| 策略 | 适用场景 |
|------|----------|
| binary_search | 大型代码库，问题位置不确定 |
| forward | 从输入开始逐步追踪 |
| backward | 从错误位置反向追踪 |
| deductive | 基于假设进行演绎推理 |
| inductive | 从观察归纳出规律 |
| divide_conquer | 复杂系统，可模块化处理 |

### 示例输出

```markdown
## 调试分析报告

### 错误分类
- **类型**: TypeError
- **严重程度**: 中等
- **语言**: Python

### 可能原因
1. 变量为 None (85% 概率)
2. 传递了错误的数据类型 (10% 概率)
3. API 响应发生变化 (5% 概率)

### 推荐策略
二分查找 - 隔离问题代码段

### 修复建议
```python
# 添加空值检查
if data is not None:
    result = data.process()
else:
    result = default_value
```
```

### 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE)

---

## Contributing

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与。

## Changelog

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本更新历史。
