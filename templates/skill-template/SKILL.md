---
name: your-skill-name
description: |
  中文描述：这个skill是做什么的，解决什么痛点，适用于什么场景
  English description: What this skill does, what pain point it solves, applicable scenarios
metadata:
  author: your-github-username
  version: 1.0.0
  category: decision-support
  tags: [decision, analysis, framework]
  license: MIT
  min_cli_version: "0.5.0"
  platforms: [windows, macos, linux]
---

# 技能中文名称 / Skill English Name

> 一句话介绍 / One-line introduction

## 简介 / Introduction

中文描述：详细介绍这个技能的功能、解决的问题、适用场景
English description: Detailed introduction of the skill's functionality, problems solved, and applicable scenarios

## 功能特性 / Features

- **核心功能1 / Core Feature 1**: 描述 / Description
- **核心功能2 / Core Feature 2**: 描述 / Description
- **核心功能3 / Core Feature 3**: 描述 / Description

## 安装 / Installation

### 方式1: CLI一键安装 / Method 1: CLI Install (Recommended)

```bash
kimi install your-skill-name
```

### 方式2: 手动安装 / Method 2: Manual Install

```bash
# 克隆仓库 / Clone repository
git clone https://github.com/your-username/your-skill-name.git

# 安装依赖 / Install dependencies
pip install -r requirements.txt

# 复制到skills目录 / Copy to skills directory
cp -r your-skill-name ~/.kimi/skills/
```

## 使用示例 / Usage Examples

### 示例1: 基础使用 / Example 1: Basic Usage

中文场景描述...
English scenario description...

```bash
# 调用示例 / Usage example
kimi skill run your-skill-name --param1 "value1" --param2 "value2"
```

**输出示例 / Output Example:**

```
中文输出结果...
English output...
```

### 示例2: 进阶使用 / Example 2: Advanced Usage

```bash
# 进阶调用 / Advanced usage
kimi skill run your-skill-name --param1 "value1" --param2 "value2" --param3 "value3"
```

## 参数说明 / Parameters

| 参数名 | 类型 | 必填 | 默认值 | 中文说明 | English Description |
|--------|------|------|--------|----------|---------------------|
| param1 | string | 是 | - | 参数1的中文说明 | Description of param1 |
| param2 | number | 否 | 50 | 参数2的中文说明 | Description of param2 |
| param3 | array | 否 | [] | 参数3的中文说明 | Description of param3 |

## 依赖要求 / Requirements

- Python 3.10+
- 依赖包 / Dependencies (see requirements.txt)

## 常见问题 / FAQ

### Q1: 问题描述 / Question?

**中文解答**: 解决方案...

**English Answer**: Solution...

### Q2: 问题描述 / Question?

**中文解答**: 解决方案...

**English Answer**: Solution...

## 更新日志 / Changelog

### v1.0.0 (YYYY-MM-DD)

- 初始发布 / Initial release
- 核心功能上线 / Core features launched

## 贡献指南 / Contributing

欢迎提交Issue和PR / Issues and PRs welcome

## 许可证 / License

MIT License - 详见 [LICENSE](./LICENSE)
