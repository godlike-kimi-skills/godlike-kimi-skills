# PDF Processor - Kimi Skill

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/python-3.8+-orange.svg" alt="Python">
</p>

<p align="center">
  <b>English</b> | <a href="#中文文档">中文</a>
</p>

---

## 📖 Overview

A powerful PDF processing skill for Kimi CLI that provides comprehensive PDF manipulation capabilities including text extraction, merging, splitting, and conversion.

### ✨ Features

- 📝 **Text Extraction** - Extract text from PDF with layout preservation
- 🔗 **PDF Merging** - Combine multiple PDFs with custom sorting
- ✂️ **PDF Splitting** - Split by page ranges or individual pages
- 🖼️ **PDF to Images** - Convert PDF pages to high-quality images
- ℹ️ **Document Info** - Retrieve PDF metadata and properties
- 🔐 **Password Support** - Handle encrypted PDF documents

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install PyPDF2>=3.0.0 pdfplumber>=0.9.0
```

### Optional Dependencies

For PDF to image conversion:

```bash
pip install pymupdf>=1.23.0
```

---

## 📚 Usage

### Using with Kimi CLI

```bash
# Extract text from PDF
kimi pdf-skill --action extract_text --input document.pdf --output text.txt

# Merge multiple PDFs
kimi pdf-skill --action merge --input ./pdf_folder/ --output merged.pdf

# Split PDF into separate pages
kimi pdf-skill --action split --input document.pdf --output ./pages/

# Extract specific pages
kimi pdf-skill --action extract_pages --input document.pdf --pages "1-5,10,15-20" --output extract.pdf

# Convert PDF to images
kimi pdf-skill --action pdf_to_images --input document.pdf --output ./images/ --dpi 300 --format png

# Get PDF information
kimi pdf-skill --action info --input document.pdf
```

### Using in Python Code

```python
from main import PDFProcessor

# Create processor instance
processor = PDFProcessor()

# Extract text
text = processor.extract_text("document.pdf")
print(text)

# Merge PDFs
processor.merge_pdfs(
    input_dir="./pdfs/",
    output_path="merged.pdf",
    sort_by="filename"
)

# Split PDF
processor.split_pdf("document.pdf", "./output/")

# Extract specific pages
processor.extract_pages(
    "document.pdf",
    "./extract.pdf",
    page_ranges=[(1, 5), (10, 10), (15, 20)]
)
```

---

## 📋 Parameter Reference

### Common Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | string | ✅ | Operation type: `extract_text`, `merge`, `split`, `extract_pages`, `pdf_to_images`, `info` |
| `input` | string | ✅ | Input file path or directory |
| `output` | string | ❌ | Output file path or directory |
| `password` | string | ❌ | PDF password for encrypted documents |

### Action-Specific Parameters

#### `extract_text`
No additional parameters.

#### `merge`
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `merge_strategy` | string | `filename` | Sort strategy: `filename` or `modified_time` |

#### `split` / `extract_pages`
| Parameter | Type | Description |
|-----------|------|-------------|
| `pages` | string | Page ranges, e.g., `1-5`, `1,3,5`, or `1-3,5,7-9` |

#### `pdf_to_images`
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dpi` | integer | 200 | Image resolution DPI |
| `format` | string | `png` | Image format: `png`, `jpg`, `jpeg`, `tiff` |

### Page Range Syntax

- `1-5` - Pages 1 through 5
- `1,3,5` - Pages 1, 3, and 5
- `1-3,5,7-9` - Pages 1-3, page 5, and pages 7-9
- `-5` - First 5 pages
- `5-` - From page 5 to end

---

## 🧪 Testing

Run the test suite:

```bash
python -m pytest tests/test_basic.py -v
```

Generate test coverage:

```bash
python -m pytest tests/test_basic.py --cov=. --cov-report=html
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📞 Support

If you encounter any issues or have questions, please file an issue on the GitHub repository.

---

---

<a name="中文文档"></a>

# PDF处理器 - Kimi 技能

<p align="center">
  <img src="https://img.shields.io/badge/版本-1.0.0-blue.svg" alt="版本">
  <img src="https://img.shields.io/badge/协议-MIT-green.svg" alt="协议">
  <img src="https://img.shields.io/badge/Python-3.8+-orange.svg" alt="Python">
</p>

<p align="center">
  <a href="#-overview">English</a> | <b>中文</b>
</p>

---

## 📖 概述

一个功能强大的Kimi CLI PDF处理技能，提供全面的PDF操作功能，包括文本提取、合并、拆分和转换。

### ✨ 功能特性

- 📝 **文本提取** - 从PDF中提取文本并保留布局
- 🔗 **PDF合并** - 将多个PDF合并，支持自定义排序
- ✂️ **PDF拆分** - 按页面范围或单页拆分
- 🖼️ **PDF转图片** - 将PDF页面转换为高质量图片
- ℹ️ **文档信息** - 获取PDF元数据和属性
- 🔐 **密码支持** - 处理加密的PDF文档

---

## 🚀 安装

### 前置要求

- Python 3.8 或更高版本
- pip 包管理器

### 安装依赖

```bash
pip install -r requirements.txt
```

或手动安装：

```bash
pip install PyPDF2>=3.0.0 pdfplumber>=0.9.0
```

### 可选依赖

用于PDF转图片功能：

```bash
pip install pymupdf>=1.23.0
```

---

## 📚 使用方法

### 在Kimi CLI中使用

```bash
# 提取PDF文本
kimi pdf-skill --action extract_text --input document.pdf --output text.txt

# 合并多个PDF
kimi pdf-skill --action merge --input ./pdf_folder/ --output merged.pdf

# 拆分PDF为单页
kimi pdf-skill --action split --input document.pdf --output ./pages/

# 提取指定页面
kimi pdf-skill --action extract_pages --input document.pdf --pages "1-5,10,15-20" --output extract.pdf

# 将PDF转为图片
kimi pdf-skill --action pdf_to_images --input document.pdf --output ./images/ --dpi 300 --format png

# 获取PDF信息
kimi pdf-skill --action info --input document.pdf
```

### 在Python代码中使用

```python
from main import PDFProcessor

# 创建处理器实例
processor = PDFProcessor()

# 提取文本
text = processor.extract_text("document.pdf")
print(text)

# 合并PDF
processor.merge_pdfs(
    input_dir="./pdfs/",
    output_path="merged.pdf",
    sort_by="filename"
)

# 拆分PDF
processor.split_pdf("document.pdf", "./output/")

# 提取指定页面
processor.extract_pages(
    "document.pdf",
    "./extract.pdf",
    page_ranges=[(1, 5), (10, 10), (15, 20)]
)
```

---

## 📋 参数说明

### 通用参数

| 参数 | 类型 | 必需 | 说明 |
|-----------|------|----------|-------------|
| `action` | string | ✅ | 操作类型：`extract_text`, `merge`, `split`, `extract_pages`, `pdf_to_images`, `info` |
| `input` | string | ✅ | 输入文件路径或目录 |
| `output` | string | ❌ | 输出文件路径或目录 |
| `password` | string | ❌ | 加密PDF的密码 |

### 各操作专用参数

#### `extract_text`
无额外参数。

#### `merge`
| 参数 | 类型 | 默认值 | 说明 |
|-----------|------|---------|-------------|
| `merge_strategy` | string | `filename` | 排序策略：`filename`（文件名）或 `modified_time`（修改时间） |

#### `split` / `extract_pages`
| 参数 | 类型 | 说明 |
|-----------|------|-------------|
| `pages` | string | 页面范围，如 `1-5`、`1,3,5` 或 `1-3,5,7-9` |

#### `pdf_to_images`
| 参数 | 类型 | 默认值 | 说明 |
|-----------|------|---------|-------------|
| `dpi` | integer | 200 | 图片分辨率DPI |
| `format` | string | `png` | 图片格式：`png`、`jpg`、`jpeg`、`tiff` |

### 页面范围语法

- `1-5` - 第1页到第5页
- `1,3,5` - 第1、3、5页
- `1-3,5,7-9` - 第1-3页、第5页、第7-9页
- `-5` - 前5页
- `5-` - 从第5页到末尾

---

## 🧪 测试

运行测试套件：

```bash
python -m pytest tests/test_basic.py -v
```

生成测试覆盖率报告：

```bash
python -m pytest tests/test_basic.py --cov=. --cov-report=html
```

---

## 📄 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。

---

## 🤝 贡献指南

欢迎贡献代码！请随时提交Pull Request。

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

---

## 📞 支持

如果遇到问题或有疑问，请在GitHub仓库提交Issue。
