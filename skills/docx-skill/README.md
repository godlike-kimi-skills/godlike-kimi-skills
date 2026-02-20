# Word文档处理器 (docx-skill)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![python-docx](https://img.shields.io/badge/python--docx-0.8.11+-green.svg)]()

[English](#english) | [中文](#中文)

---

## English

### Overview

**docx-skill** is a Kimi CLI skill for automating Microsoft Word document processing. Create, edit, format, and merge Word documents without manual intervention.

### Features

- 📝 **Create documents** from Markdown, JSON, or plain text
- ✏️ **Edit existing documents** - modify content and styles
- 🎨 **Use templates** for standardized document generation
- 🔗 **Merge documents** - combine multiple files into one
- 🔄 **Format conversion** - support multiple input formats

### Installation

```bash
kimi skill install https://github.com/godlike-kimi-skills/docx-skill
```

### Quick Start

```bash
# Create a simple document
kimi skill run docx-skill --params "action=create&output=document.docx&content=Hello World"

# Convert Markdown to Word
kimi skill run docx-skill --params "action=create&output=report.docx&input=report.md"

# Use template
kimi skill run docx-skill --params "action=template&template=template.docx&output=output.docx"
```

### Usage Examples

#### Create from Markdown
```bash
kimi skill run docx-skill --params "action=create&output=document.docx&input=content.md"
```

#### Create with JSON content
```bash
kimi skill run docx-skill --params "action=create&output=document.docx&content={\"title\":\"My Doc\",\"body\":\"Content\"}"
```

#### Merge documents
```bash
kimi skill run docx-skill --params "action=merge&input=doc1.docx,doc2.docx&output=merged.docx"
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | string | Yes | Operation: create/edit/merge/template |
| `input` | string | Conditional | Input file path(s) |
| `output` | string | Yes | Output file path |
| `content` | string | Conditional | Document content |
| `template` | string | Conditional | Template file path |

### Requirements

- Python 3.10+
- python-docx >= 0.8.11

### License

MIT License - see [LICENSE](LICENSE) for details

---

## 中文

### 简介

**docx-skill** 是一个 Kimi CLI 技能，用于自动化 Microsoft Word 文档处理。无需手动操作，即可创建、编辑、格式化和合并 Word 文档。

### 特性

- 📝 **创建文档** - 从 Markdown、JSON 或纯文本生成
- ✏️ **编辑文档** - 修改内容和样式
- 🎨 **使用模板** - 标准化文档生成
- 🔗 **合并文档** - 多个文件合并为一个
- 🔄 **格式转换** - 支持多种输入格式

### 安装

```bash
kimi skill install https://github.com/godlike-kimi-skills/docx-skill
```

### 快速开始

```bash
# 创建简单文档
kimi skill run docx-skill --params "action=create&output=document.docx&content=Hello World"

# Markdown 转 Word
kimi skill run docx-skill --params "action=create&output=report.docx&input=report.md"

# 使用模板
kimi skill run docx-skill --params "action=template&template=template.docx&output=output.docx"
```

### 使用示例

#### 从 Markdown 创建
```bash
kimi skill run docx-skill --params "action=create&output=document.docx&input=content.md"
```

#### JSON 内容创建
```bash
kimi skill run docx-skill --params "action=create&output=document.docx&content={\"title\":\"My Doc\",\"body\":\"Content\"}"
```

#### 合并文档
```bash
kimi skill run docx-skill --params "action=merge&input=doc1.docx,doc2.docx&output=merged.docx"
```

### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `action` | string | 是 | 操作类型 |
| `input` | string | 条件 | 输入文件路径 |
| `output` | string | 是 | 输出文件路径 |
| `content` | string | 条件 | 文档内容 |
| `template` | string | 条件 | 模板文件路径 |

### 环境要求

- Python 3.10+
- python-docx >= 0.8.11

### 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## Roadmap

- [x] v1.0.0 - Basic document creation
- [ ] v1.1.0 - Advanced formatting options
- [ ] v1.2.0 - Image handling improvements
- [ ] v1.3.0 - Macro support

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

**Made with ❤️ by Godlike Kimi Skills Team**

[GitHub](https://github.com/godlike-kimi-skills) | [Issues](https://github.com/godlike-kimi-skills/docx-skill/issues) | [Discussions](https://github.com/godlike-kimi-skills/docx-skill/discussions)
