# Test-Driven Development (TDD) Skill

<div align="center">

🎯 **Methodology Guidance** | 📝 **Test Generation** | 📊 **Coverage Analysis** | 🧩 **Template Creation**

[English](#english) | [中文](#中文)

</div>

---

<a name="english"></a>
## 🇬🇧 English

### Overview

The **TDD Skill** provides comprehensive **Test-Driven Development** methodology guidance to help developers build high-quality software following TDD best practices.

TDD is a software development methodology with the core principle: **Write tests first, then write code**. Through short cycles of "Red-Green-Refactor", you gradually build reliable software.

### Features

| Feature | Description |
|---------|-------------|
| 🎯 **TDD Workflow Guide** | Complete methodology guidance and best practices |
| 📝 **Test Case Generation** | Generate test case suggestions based on feature descriptions |
| 📊 **Code Coverage Analysis** | Analyze test coverage and provide improvement suggestions |
| 🧩 **Test Template Generation** | Generate test templates for multiple languages and frameworks |
| 🔄 **Red-Green-Refactor Guide** | Detailed cycle guidance to master TDD rhythm |

### Supported Languages and Frameworks

| Language | Supported Frameworks |
|----------|---------------------|
| Python | pytest, unittest |
| JavaScript | Jest, Mocha |
| TypeScript | Jest |
| Java | JUnit, TestNG |
| Go | Built-in testing |
| Rust | Built-in testing |
| C++ | Google Test, Catch2 |

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd test-driven-development

# Install dependencies
pip install -r requirements.txt
```

### Quick Start

#### 1. Get TDD Workflow Guide

```bash
python main.py --action workflow --language python --feature "Implement user login"
```

#### 2. Generate Test Cases

```bash
python main.py --action generate \
  --language python \
  --test_framework pytest \
  --feature "Calculate shopping cart total with discount and tax"
```

#### 3. Generate Test Template

```bash
python main.py --action template \
  --language python \
  --test_framework pytest \
  --class_name Calculator \
  --method_name add \
  --output_dir ./tests
```

#### 4. Coverage Analysis

```bash
python main.py --action coverage \
  --file_path src/calculator.py \
  --test_file_path tests/test_calculator.py \
  --coverage_threshold 85
```

#### 5. Red-Green-Refactor Guide

```bash
python main.py --action red-green-refactor
```

### The TDD Cycle (Red-Green-Refactor)

```
┌─────────┐    ┌─────────┐    ┌─────────┐
│ Write   │ →  │ Run     │ →  │ See     │
│ Test    │    │ Test    │    │ Fail    │
└─────────┘    └────┬────┘    └────┬────┘
     ↑              │ FAIL         │
     │              ↓              │
┌────┴────┐    ┌─────────┐         │
│Refactor │ ←  │ See     │         │
│ Code    │    │ Pass    │         │
└────┬────┘    └────┬────┘         │
     ↑           PASS│              │
     │              ↓               │
     └──────── ┌─────────┐ ←───────┘
               │ Write   │
               │ Code    │
               └─────────┘
```

### Key Principles

1. **Test First**: Write tests before implementation
2. **Small Steps**: Focus on one small feature at a time
3. **Fast Feedback**: Verify correctness through tests quickly
4. **Continuous Refactoring**: Optimize code under test protection

### Parameters

| Parameter | Short | Type | Required | Default | Description |
|-----------|-------|------|----------|---------|-------------|
| --action | -a | string | Yes | - | Action type |
| --language | -l | string | No | python | Programming language |
| --test_framework | -f | string | No | pytest | Testing framework |
| --feature | -e | string | No | "" | Feature description |
| --file_path | -s | string | No | "" | Source file path |
| --test_file_path | -t | string | No | "" | Test file path |
| --output_dir | -o | string | No | ./tests | Output directory |
| --coverage_threshold | -c | float | No | 80.0 | Coverage threshold |

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage report
pytest tests/ --cov=. --cov-report=html
```

### License

MIT License - See [LICENSE](LICENSE) file for details

---

<a name="中文"></a>
## 🇨🇳 中文

### 简介

**TDD Skill** 提供完整的**测试驱动开发 (Test-Driven Development)** 方法论指导，帮助开发者遵循TDD最佳实践进行软件开发。

TDD是一种软件开发方法论，核心思想是：**先写测试，后写代码**，通过短周期的"红-绿-重构"循环逐步构建高质量的软件。

### 核心功能

| 功能 | 描述 |
|------|------|
| 🎯 **TDD工作流指导** | 完整的方法论指导和最佳实践 |
| 📝 **测试用例生成** | 基于功能描述生成测试用例建议 |
| 📊 **代码覆盖率分析** | 分析测试覆盖率，提供改进建议 |
| 🧩 **测试模板生成** | 为多种语言和框架生成测试模板 |
| 🔄 **红绿重构指导** | 详细的循环指导，帮助掌握TDD节奏 |

### 支持的语言和框架

| 语言 | 支持的测试框架 |
|------|---------------|
| Python | pytest, unittest |
| JavaScript | Jest, Mocha |
| TypeScript | Jest |
| Java | JUnit, TestNG |
| Go | 内置测试框架 |
| Rust | 内置测试框架 |
| C++ | Google Test, Catch2 |

### 安装

```bash
# 克隆仓库
git clone <repository-url>
cd test-driven-development

# 安装依赖
pip install -r requirements.txt
```

### 快速开始

#### 1. 获取TDD工作流指导

```bash
python main.py --action workflow --language python --feature "实现用户登录功能"
```

#### 2. 生成测试用例

```bash
python main.py --action generate \
  --language python \
  --test_framework pytest \
  --feature "计算购物车总价，包括折扣和税费"
```

#### 3. 生成测试模板

```bash
python main.py --action template \
  --language python \
  --test_framework pytest \
  --class_name Calculator \
  --method_name add \
  --output_dir ./tests
```

#### 4. 覆盖率分析

```bash
python main.py --action coverage \
  --file_path src/calculator.py \
  --test_file_path tests/test_calculator.py \
  --coverage_threshold 85
```

#### 5. 红绿重构指导

```bash
python main.py --action red-green-refactor
```

### TDD循环（红-绿-重构）

```
┌─────────┐    ┌─────────┐    ┌─────────┐
│  编写    │ → │  运行    │ → │  看到    │
│  测试    │    │  测试    │    │  失败    │
└─────────┘    └────┬────┘    └────┬────┘
     ↑              │ FAIL         │
     │              ↓              │
┌────┴────┐    ┌─────────┐         │
│  重构    │ ← │  看到    │         │
│  代码    │    │  通过    │         │
└────┬────┘    └────┬────┘         │
     ↑           PASS│              │
     │              ↓               │
     └──────── ┌─────────┐ ←───────┘
               │  编写    │
               │  代码    │
               └─────────┘
```

### 核心原则

1. **测试优先**：先写测试，后写实现
2. **小步快跑**：每次只关注一个小功能点
3. **快速反馈**：通过测试快速验证代码正确性
4. **持续重构**：在测试保护下不断优化代码

### 参数说明

| 参数 | 简写 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|------|--------|------|
| --action | -a | string | 是 | - | 操作类型 |
| --language | -l | string | 否 | python | 编程语言 |
| --test_framework | -f | string | 否 | pytest | 测试框架 |
| --feature | -e | string | 否 | "" | 功能描述 |
| --file_path | -s | string | 否 | "" | 源代码文件路径 |
| --test_file_path | -t | string | 否 | "" | 测试文件路径 |
| --output_dir | -o | string | 否 | ./tests | 输出目录 |
| --coverage_threshold | -c | float | 否 | 80.0 | 覆盖率阈值 |

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行测试并生成覆盖率报告
pytest tests/ --cov=. --cov-report=html
```

### 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

<div align="center">

**Made with ❤️ for better software development**

</div>
