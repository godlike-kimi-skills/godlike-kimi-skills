# Excel Processor (xlsx-skill)

A comprehensive Kimi Skill for Excel file manipulation with support for reading, writing, formatting, formulas, and charts.

Excel处理器 - 一个功能完善的Kimi Skill，用于Excel文件的读取、写入、格式化、公式计算和图表生成。

---

## 📋 Table of Contents | 目录

- [Features | 功能特性](#features--功能特性)
- [Installation | 安装](#installation--安装)
- [Usage | 使用方法](#usage--使用方法)
- [Parameters | 参数说明](#parameters--参数说明)
- [Examples | 使用示例](#examples--使用示例)
- [API Reference | API参考](#api-reference--api参考)
- [License | 许可证](#license--许可证)

---

## Features | 功能特性

**English:**
- 📖 **Read Excel**: Extract data from Excel files with range and header options
- ✍️ **Write Excel**: Write data in dictionary or list format
- ➕ **Append Data**: Add rows to existing worksheets
- 🔗 **Merge Files**: Combine multiple Excel files
- 🎨 **Formatting**: Customize fonts, colors, alignment, and borders
- 🧮 **Formulas**: Insert Excel formulas into cells
- 📊 **Charts**: Generate bar, line, pie, and scatter charts

**中文：**
- 📖 **读取Excel**: 从Excel文件提取数据，支持范围和表头选项
- ✍️ **写入Excel**: 以字典或列表格式写入数据
- ➕ **追加数据**: 向现有工作表添加行
- 🔗 **合并文件**: 合并多个Excel文件
- 🎨 **格式化**: 自定义字体、颜色、对齐方式和边框
- 🧮 **公式**: 在单元格中插入Excel公式
- 📊 **图表**: 生成柱状图、折线图、饼图和散点图

---

## Installation | 安装

```bash
# Clone the repository | 克隆仓库
git clone https://github.com/godlike-kimi/skills/xlsx-skill.git
cd xlsx-skill

# Install dependencies | 安装依赖
pip install -r requirements.txt
```

**Requirements | 环境要求:**
- Python 3.7 or higher
- openpyxl >= 3.1.0

---

## Usage | 使用方法

### Command Line | 命令行

```bash
python main.py <action> [options]
```

### As Python Library | 作为Python库

```python
from main import ExcelProcessor

# Initialize | 初始化
processor = ExcelProcessor('data.xlsx')

# Read data | 读取数据
data = processor.read(sheet_name='Sheet1')

# Write data | 写入数据
processor.write([
    {'name': 'John', 'age': 30},
    {'name': 'Jane', 'age': 25}
])

# Save | 保存
processor.save()
```

---

## Parameters | 参数说明

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| action | string | Yes | Operation type: read/write/append/merge/format/chart/formula |
| input | string | No | Input file path |
| output | string | No | Output file path |
| sheet | string | No | Sheet name, default: Sheet1 |
| data | string | No | JSON data string |
| range | string | No | Cell range, e.g., A1:D10 |
| headers | boolean | No | Include headers, default: true |
| chart_type | string | No | Chart type: bar/line/pie/scatter |
| title | string | No | Chart title |
| formula | string | No | Excel formula |
| cell | string | No | Cell reference |
| font | string | No | Font settings (JSON) |
| fill | string | No | Fill settings (JSON) |
| alignment | string | No | Alignment settings (JSON) |

---

## Examples | 使用示例

### 1. Read Excel | 读取Excel

```bash
# Read entire sheet | 读取整个工作表
python main.py read --input data.xlsx

# Read specific range | 读取指定范围
python main.py read --input data.xlsx --range A1:D10

# Without headers | 不包含表头
python main.py read --input data.xlsx --headers false
```

**Output | 输出:**
```json
[
  {"name": "John", "age": 30, "city": "New York"},
  {"name": "Jane", "age": 25, "city": "London"}
]
```

### 2. Write Data | 写入数据

```bash
# Write object array | 写入对象数组
python main.py write --input output.xlsx \
  --data '[{"name":"John","age":30},{"name":"Jane","age":25}]'

# Write 2D array | 写入二维数组
python main.py write --input output.xlsx \
  --data '[["Name","Age"],["John",30],["Jane",25]]'
```

### 3. Format Cells | 格式化单元格

```bash
# Set background color | 设置背景色
python main.py format --input data.xlsx --range A1:D1 \
  --fill '{"color":"4472C4"}'

# Set font | 设置字体
python main.py format --input data.xlsx --range A1:D10 \
  --font '{"bold":true,"size":12,"color":"FFFFFF"}'

# Set alignment | 设置对齐
python main.py format --input data.xlsx --range A1:D10 \
  --alignment '{"horizontal":"center","vertical":"center"}'
```

### 4. Add Formulas | 添加公式

```bash
# Sum formula | 求和公式
python main.py formula --input data.xlsx --cell E11 \
  --formula "=SUM(E2:E10)"

# Average formula | 平均值公式
python main.py formula --input data.xlsx --cell F11 \
  --formula "=AVERAGE(F2:F10)"
```

### 5. Create Charts | 创建图表

```bash
# Bar chart | 柱状图
python main.py chart --input data.xlsx --chart_type bar \
  --title "Sales Report"

# Line chart | 折线图
python main.py chart --input data.xlsx --chart_type line \
  --title "Trend Analysis"

# Pie chart | 饼图
python main.py chart --input data.xlsx --chart_type pie \
  --title "Market Share"
```

### 6. Merge Files | 合并文件

```bash
# Vertical merge | 垂直合并
python main.py merge \
  --files "jan.xlsx,feb.xlsx,mar.xlsx" \
  --output quarterly.xlsx
```

---

## API Reference | API参考

### ExcelProcessor Class

#### Methods

| Method | Description | Parameters |
|--------|-------------|------------|
| `read()` | Read data from Excel | sheet_name, cell_range, headers |
| `write()` | Write data to Excel | data, sheet_name, headers, start_cell |
| `append()` | Append a row | data, sheet_name |
| `merge_files()` | Merge multiple files | files, output, merge_type |
| `format_cells()` | Format cell range | cell_range, sheet_name, font, fill, alignment, border |
| `add_formula()` | Add formula | cell, formula, sheet_name |
| `create_chart()` | Create chart | chart_type, data_range, title, sheet_name, target_sheet |
| `save()` | Save workbook | output_path |

---

## Format Options | 格式选项

### Font | 字体

```json
{
  "name": "Arial",
  "size": 12,
  "bold": true,
  "italic": false,
  "color": "FF0000"
}
```

### Fill | 填充

```json
{
  "color": "FFFF00",
  "type": "solid"
}
```

### Alignment | 对齐

```json
{
  "horizontal": "center",
  "vertical": "center",
  "wrap_text": true
}
```

**Horizontal | 水平:** `left`, `center`, `right`

**Vertical | 垂直:** `top`, `center`, `bottom`

---

## Testing | 测试

```bash
# Run tests | 运行测试
python -m pytest tests/test_basic.py -v
```

---

## License | 许可证

MIT License - see [LICENSE](LICENSE) file for details.

---

## Contributing | 贡献

Contributions are welcome! Please feel free to submit a Pull Request.

欢迎贡献！请随时提交Pull Request。

---

## Support | 支持

- GitHub Issues: [https://github.com/godlike-kimi/skills/issues](https://github.com/godlike-kimi/skills/issues)
- Documentation: [SKILL.md](SKILL.md)

---

<p align="center">Made with ❤️ by godlike-kimi</p>
