# Skill Creator Enhanced

> One-click generator for production-ready Kimi Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Kimi CLI](https://img.shields.io/badge/Kimi%20CLI-0.5.0+-green.svg)]()

[English](#english) | [中文](#中文)

---

## English

### Overview

**Skill Creator Enhanced** is a CLI tool that generates production-ready Kimi Skill projects following the **Anthropic Agent Skill Standard** and **Godlike Kimi Skills Specification**.

### Features

- ⚡ **One-click scaffolding** - Complete project structure in seconds
- 📋 **Standardized templates** - skill.json, SKILL.md, README.md, LICENSE
- 🧪 **Test templates** - pytest unit test framework
- 🚀 **CI/CD ready** - GitHub Actions workflows
- ✅ **Validation** - Check compliance with open source standards

### Quick Start

```bash
# Install (via Kimi CLI)
kimi skill install https://github.com/godlike-kimi-skills/skill-creator-enhanced

# Create a new skill
kimi skill run skill-creator-enhanced \
  --params "action=create&skill_name=web-scraper&skill_title=Web Scraper&description=Extract structured data from websites"
```

### Generated Project Structure

```
my-skill/
├── skill.json           # Skill manifest
├── SKILL.md             # Usage documentation
├── README.md            # GitHub homepage
├── LICENSE              # MIT license
├── main.py              # Entry point
├── requirements.txt     # Dependencies
├── tests/               # Test suite
├── examples/            # Usage examples
└── .github/workflows/   # CI/CD configs
```

### Usage Examples

#### Create a Data Processing Skill
```bash
kimi skill run skill-creator-enhanced \
  --params "action=create&skill_name=csv-processor&category=data"
```

#### Validate Existing Skill
```bash
kimi skill run skill-creator-enhanced \
  --params "action=validate&skill_path=./my-skill"
```

### Available Templates

| Template | Description |
|----------|-------------|
| `basic` | Minimal skill template |
| `cli-tool` | Command-line tool |
| `api-service` | API service wrapper |
| `data-processor` | Data processing pipeline |
| `automation` | Automation task |

### Requirements

- Python 3.10+
- Kimi Code CLI 0.5.0+

### License

MIT License - see [LICENSE](LICENSE) for details

---

## 中文

### 简介

**增强版技能创建器** 是一个命令行工具，用于生成符合 **Anthropic Agent Skill 标准** 和 **Godlike Kimi Skills 规范** 的生产级 Kimi Skill 项目。

### 特性

- ⚡ **一键脚手架** - 秒级生成完整项目结构
- 📋 **标准化模板** - skill.json、SKILL.md、README.md、LICENSE
- 🧪 **测试模板** - pytest 单元测试框架
- 🚀 **CI/CD 就绪** - GitHub Actions 工作流
- ✅ **合规验证** - 检查是否符合开源标准

### 快速开始

```bash
# 安装（通过 Kimi CLI）
kimi skill install https://github.com/godlike-kimi-skills/skill-creator-enhanced

# 创建新技能
kimi skill run skill-creator-enhanced \
  --params "action=create&skill_name=web-scraper&skill_title=网页抓取器&description=从网站提取结构化数据"
```

### 生成的项目结构

```
my-skill/
├── skill.json           # Skill 清单
├── SKILL.md             # 使用文档
├── README.md            # GitHub 主页
├── LICENSE              # MIT 许可证
├── main.py              # 入口文件
├── requirements.txt     # 依赖
├── tests/               # 测试套件
├── examples/            # 使用示例
└── .github/workflows/   # CI/CD 配置
```

### 使用示例

#### 创建数据处理技能
```bash
kimi skill run skill-creator-enhanced \
  --params "action=create&skill_name=csv-processor&category=data"
```

#### 验证现有技能
```bash
kimi skill run skill-creator-enhanced \
  --params "action=validate&skill_path=./my-skill"
```

### 可用模板

| 模板 | 描述 |
|------|------|
| `basic` | 最小化技能模板 |
| `cli-tool` | 命令行工具 |
| `api-service` | API 服务包装 |
| `data-processor` | 数据处理管道 |
| `automation` | 自动化任务 |

### 环境要求

- Python 3.10+
- Kimi Code CLI 0.5.0+

### 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## Roadmap

- [x] v1.0.0 - Core scaffolding functionality
- [ ] v1.1.0 - More templates (FastAPI, Flask, etc.)
- [ ] v1.2.0 - Interactive mode
- [ ] v1.3.0 - Skill marketplace integration

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

**Made with ❤️ by Godlike Kimi Skills Team**

[GitHub](https://github.com/godlike-kimi-skills) | [Issues](https://github.com/godlike-kimi-skills/skill-creator-enhanced/issues) | [Discussions](https://github.com/godlike-kimi-skills/skill-creator-enhanced/discussions)
