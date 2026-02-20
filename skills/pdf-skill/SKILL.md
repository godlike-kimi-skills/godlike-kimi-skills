# PDF处理器 (PDF Processor)

一个功能强大的PDF处理技能，支持文本提取、文档合并、页面拆分、PDF转图片等操作。

## 功能概述

| 功能 | 描述 |
|------|------|
| `extract_text` | 从PDF中提取文本内容 |
| `merge` | 合并多个PDF文件 |
| `split` | 按页面拆分PDF为多个文件 |
| `extract_pages` | 提取指定页面范围 |
| `pdf_to_images` | 将PDF页面转换为图片 |
| `info` | 获取PDF文档信息 |

## 使用方法

### 在Kimi CLI中使用

```bash
# 提取PDF文本
kimi pdf-skill --action extract_text --input document.pdf --output text.txt

# 合并PDF文件
kimi pdf-skill --action merge --input ./pdf_folder/ --output merged.pdf

# 拆分PDF
kimi pdf-skill --action split --input document.pdf --output ./pages/

# 提取指定页面
kimi pdf-skill --action extract_pages --input document.pdf --pages "1-5,10,15-20" --output extract.pdf

# PDF转图片
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

# 提取页面
processor.extract_pages(
    "document.pdf",
    "./extract.pdf",
    page_ranges=[(1, 5), (10, 10), (15, 20)]
)

# 转图片
processor.pdf_to_images(
    "document.pdf",
    "./images/",
    dpi=300,
    fmt="png"
)

# 获取信息
info = processor.get_info("document.pdf")
print(info)
```

## 参数说明

### 通用参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `action` | string | ✅ | 操作类型 |
| `input` | string | ✅ | 输入文件或目录路径 |
| `output` | string | ❌ | 输出文件或目录路径 |
| `password` | string | ❌ | PDF密码（用于加密文档） |

### 各操作专用参数

#### extract_text
- 无专用参数

#### merge
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `merge_strategy` | string | `filename` | 排序策略：`filename`（文件名）或 `modified_time`（修改时间） |

#### split / extract_pages
| 参数 | 类型 | 说明 |
|------|------|------|
| `pages` | string | 页面范围，如 `1-5` 或 `1,3,5` 或 `1-3,5,7-9` |

#### pdf_to_images
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `dpi` | integer | 200 | 图片分辨率 |
| `format` | string | `png` | 图片格式：`png`, `jpg`, `jpeg`, `tiff` |

## 页面范围语法

支持多种页面范围格式：

- `1-5` - 第1页到第5页
- `1,3,5` - 第1、3、5页
- `1-3,5,7-9` - 第1-3页、第5页、第7-9页
- `-5` - 前5页
- `5-` - 从第5页到末尾

## 示例场景

### 场景1：批量提取合同文本

```bash
for file in contracts/*.pdf; do
    kimi pdf-skill --action extract_text --input "$file" --output "texts/$(basename $file .pdf).txt"
done
```

### 场景2：合并扫描文档

```bash
kimi pdf-skill --action merge --input ./scanned_pages/ --output final_document.pdf --merge_strategy filename
```

### 场景3：提取报告中的图表页面

```bash
kimi pdf-skill --action extract_pages --input report.pdf --pages "5-12,25-30" --output charts_section.pdf
```

### 场景4：将PDF转换为图片用于演示

```bash
kimi pdf-skill --action pdf_to_images --input presentation.pdf --output ./slides/ --dpi 300 --format png
```

## 注意事项

1. **密码保护**：处理加密PDF时需要提供`password`参数
2. **大文件处理**：超大PDF建议分页处理以避免内存不足
3. **图片转换**：需要安装`pymupdf`或`pdf2image`库
4. **文本提取**：扫描版PDF需要OCR才能提取文本

## 依赖项

- Python >= 3.8
- PyPDF2 >= 3.0.0
- pdfplumber >= 0.9.0
- (可选) pymupdf >= 1.23.0 - 用于PDF转图片

## 许可证

MIT License - 详见 LICENSE 文件
