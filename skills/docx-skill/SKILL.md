# Word文档处理器 (docx-skill)

> 创建、编辑、格式化 Word 文档 (.docx)，支持模板、表格、图片插入和文档合并

---

## 功能概述

本 Skill 让你能够通过 Kimi CLI 自动化处理 Word 文档，无需手动操作 Microsoft Word。

### 核心能力

1. **创建文档** - 从 Markdown、JSON 或纯文本生成 Word 文档
2. **编辑文档** - 修改现有文档的内容、样式和结构
3. **使用模板** - 基于模板快速生成标准化文档
4. **合并文档** - 将多个文档合并为一个
5. **转换格式** - 支持多种输入格式转换

---

## 使用方法

### 基础用法

```bash
# 创建简单文档
kimi skill run docx-skill --params "action=create&output=document.docx&content=Hello World"

# 从 Markdown 创建文档
kimi skill run docx-skill --params "action=create&output=report.docx&input=report.md"

# 使用模板
kimi skill run docx-skill --params "action=template&template=template.docx&output=document.docx&content={\"name\":\"张三\"}"
```

### 进阶用法

```bash
# 创建带表格的文档
kimi skill run docx-skill --params "action=create&output=table.docx&content={\"title\":\"数据表\",\"table\":[[\"姓名\",\"年龄\"],[\"张三\",25]]}"

# 合并多个文档
kimi skill run docx-skill --params "action=merge&input=doc1.docx,doc2.docx,doc3.docx&output=merged.docx"

# 编辑现有文档
kimi skill run docx-skill --params "action=edit&input=existing.docx&output=edited.docx&content={\"replace\":{\"old\":\"new\"}}"
```

---

## 参数说明

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|-------|------|------|-------|------|
| `action` | string | 是 | - | 操作类型: create/edit/merge/template/convert |
| `input` | string | 条件 | - | 输入文件路径（多个用逗号分隔） |
| `output` | string | 是 | - | 输出文件路径 |
| `content` | string | 条件 | - | 文档内容或修改指令 |
| `template` | string | 条件 | - | 模板文件路径 |
| `styles` | string | 否 | - | 样式配置（JSON格式） |

---

## 示例

### 示例1：创建简单文档

```bash
kimi skill run docx-skill --params "action=create&output=hello.docx&content=这是一份简单的Word文档"
```

### 示例2：从 Markdown 创建报告

创建 `report.md`:
```markdown
# 项目报告

## 概述
这是项目概述部分。

## 数据
| 项目 | 数值 |
|------|------|
| 完成度 | 85% |
| 质量 | 优秀 |
```

转换:
```bash
kimi skill run docx-skill --params "action=create&output=report.docx&input=report.md"
```

### 示例3：使用 JSON 内容创建复杂文档

```bash
kimi skill run docx-skill --params "action=create&output=complex.docx&content={
  \"title\": \"产品说明书\",
  \"sections\": [
    {\"heading\": \"产品介绍\", \"content\": \"这是产品介绍...\"},
    {\"heading\": \"技术规格\", \"content\": \"规格参数...\"}
  ],
  \"table\": {
    \"headers\": [\"参数\", \"数值\"],
    \"rows\": [[\"尺寸\", \"100x100\"], [\"重量\", \"500g\"]]
  }
}"
```

### 示例4：批量生成证书

```bash
# 准备数据文件 names.txt（每行一个姓名）
# 准备模板 certificate-template.docx

kimi skill run docx-skill --params "action=template&template=certificate-template.docx&input=names.txt&output=certificates/"
```

---

## 技术细节

### 依赖要求
- Python 3.10+
- python-docx >= 0.8.11

### 支持的输入格式
- Markdown (.md)
- 纯文本 (.txt)
- JSON (.json)
- HTML (.html) - 基础支持

### 功能特性

#### 创建文档
- ✅ 标题和段落
- ✅ 无序/有序列表
- ✅ 表格
- ✅ 图片插入
- ✅ 页眉页脚
- ✅ 样式定制

#### 编辑文档
- ✅ 文本替换
- ✅ 添加内容
- ✅ 删除内容
- ✅ 修改样式
- ✅ 插入表格/图片

#### 模板功能
- ✅ 变量替换
- ✅ 条件内容
- ✅ 循环生成（批量处理）

---

## 更新日志

### v1.0.0 (2026-02-20)
- 初始版本发布
- 基础文档创建功能
- 模板支持
- 文档合并功能

---

**Made with ❤️ by Godlike Kimi Skills**
