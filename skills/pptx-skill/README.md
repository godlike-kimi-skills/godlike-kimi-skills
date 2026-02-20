# PPT处理器 | PowerPoint Processor

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](https://github.com/godlike-kimi/pptx-skill)

[English](#english) | [中文](#中文)

---

<a name="中文"></a>
## 中文

一个功能强大的PowerPoint演示文稿处理工具，支持从Markdown/JSON创建PPT、模板应用、图表插入和图片处理。

### 特性

- 📝 **多格式支持** - 从Markdown、JSON或Python代码创建PPT
- 🎨 **丰富模板** - 内置5+专业主题模板
- 📊 **数据可视化** - 支持柱状图、折线图、饼图等
- 🖼️ **图片处理** - 自动调整大小、裁剪和定位
- 🔧 **批量操作** - 合并、拆分多个PPT文件
- 🌐 **多平台** - 支持Windows、Linux、macOS

### 安装

```bash
# 克隆仓库
git clone https://github.com/godlike-kimi/pptx-skill.git
cd pptx-skill

# 安装依赖
pip install -r requirements.txt
```

### 快速开始

```bash
# 从Markdown创建PPT
python main.py --action create --input "# 标题\n\n内容" --output output.pptx

# 使用模板
python main.py --action create --input content.md --template business --output report.pptx

# 通过Kimi CLI使用
kimi skill pptx-skill --action create --input presentation.md --output slides.pptx
```

### 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| action | string | 是 | - | 操作类型：create/edit/merge/split/convert/template |
| input | string | 否 | - | 输入文件路径或内容字符串 |
| output | string | 否 | output.pptx | 输出文件路径 |
| template | string | 否 | default | 模板名称或路径 |
| theme | string | 否 | default | 主题：default/dark/light/blue/green |
| slides | array | 否 | [] | 幻灯片内容数组 |
| charts | object | 否 | {} | 图表配置对象 |
| images | array | 否 | [] | 图片路径数组 |

### Markdown格式

```markdown
# 幻灯片标题

- 要点1
- 要点2

---

# 第二页

正文内容
```

### JSON格式

```json
{
  "title": "演示文稿",
  "slides": [
    {
      "title": "第一页",
      "content": ["要点1", "要点2"],
      "layout": "title_and_content"
    }
  ]
}
```

### Python API

```python
from main import PPTXSkill

skill = PPTXSkill()

# 创建PPT
skill.create_from_markdown("input.md", "output.pptx", template="modern")

# 添加幻灯片
skill.add_slide(title="新页面", content=["内容1", "内容2"])

# 插入图表
skill.add_chart(
    slide_index=1,
    chart_type="bar",
    data={"labels": ["A", "B"], "values": [10, 20]}
)

# 保存
skill.save("output.pptx")
```

### 内置模板

- `default` - 默认白色主题
- `business` - 商务蓝主题  
- `dark` - 深色主题
- `minimal` - 极简风格
- `colorful` - 多彩设计

---

<a name="english"></a>
## English

A powerful PowerPoint presentation processing tool that supports creating PPTs from Markdown/JSON, template application, chart insertion, and image processing.

### Features

- 📝 **Multi-format Support** - Create PPTs from Markdown, JSON, or Python code
- 🎨 **Rich Templates** - Built-in 5+ professional theme templates
- 📊 **Data Visualization** - Support for bar charts, line charts, pie charts, etc.
- 🖼️ **Image Processing** - Auto-resize, crop, and positioning
- 🔧 **Batch Operations** - Merge and split multiple PPT files
- 🌐 **Cross-platform** - Support Windows, Linux, macOS

### Installation

```bash
# Clone repository
git clone https://github.com/godlike-kimi/pptx-skill.git
cd pptx-skill

# Install dependencies
pip install -r requirements.txt
```

### Quick Start

```bash
# Create PPT from Markdown
python main.py --action create --input "# Title\n\nContent" --output output.pptx

# Use template
python main.py --action create --input content.md --template business --output report.pptx

# Use via Kimi CLI
kimi skill pptx-skill --action create --input presentation.md --output slides.pptx
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| action | string | Yes | - | Operation: create/edit/merge/split/convert/template |
| input | string | No | - | Input file path or content string |
| output | string | No | output.pptx | Output file path |
| template | string | No | default | Template name or path |
| theme | string | No | default | Theme: default/dark/light/blue/green |
| slides | array | No | [] | Slides content array |
| charts | object | No | {} | Chart configuration object |
| images | array | No | [] | Image paths array |

### Markdown Format

```markdown
# Slide Title

- Bullet 1
- Bullet 2

---

# Second Slide

Body content
```

### JSON Format

```json
{
  "title": "Presentation",
  "slides": [
    {
      "title": "First Slide",
      "content": ["Point 1", "Point 2"],
      "layout": "title_and_content"
    }
  ]
}
```

### Python API

```python
from main import PPTXSkill

skill = PPTXSkill()

# Create PPT
skill.create_from_markdown("input.md", "output.pptx", template="modern")

# Add slide
skill.add_slide(title="New Page", content=["Content 1", "Content 2"])

# Insert chart
skill.add_chart(
    slide_index=1,
    chart_type="bar",
    data={"labels": ["A", "B"], "values": [10, 20]}
)

# Save
skill.save("output.pptx")
```

### Built-in Templates

- `default` - Default white theme
- `business` - Business blue theme
- `dark` - Dark theme
- `minimal` - Minimalist style
- `colorful` - Colorful design

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.
