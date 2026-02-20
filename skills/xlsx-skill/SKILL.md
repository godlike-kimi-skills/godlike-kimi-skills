# Excel处理器 (xlsx-skill)

一个功能强大的Excel文件处理Kimi Skill，支持读取、写入、格式化、公式和图表功能。

## 功能概述

- **读取Excel**: 从Excel文件读取数据，支持指定范围和表头
- **写入Excel**: 将数据写入Excel，支持字典和列表格式
- **追加数据**: 在现有工作表中追加行
- **合并文件**: 合并多个Excel文件
- **格式化**: 设置单元格字体、颜色、对齐方式和边框
- **添加公式**: 在单元格中插入Excel公式
- **创建图表**: 生成柱状图、折线图、饼图和散点图

## 使用方法

### 作为命令行工具

```bash
python main.py <action> [options]
```

### 作为Python库

```python
from main import ExcelProcessor

processor = ExcelProcessor('data.xlsx')
data = processor.read()
processor.write([{'name': '张三', 'age': 25}])
processor.save()
```

## 参数说明

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| action | string | 是 | 操作类型: read/write/append/merge/format/chart/formula |
| input | string | 否 | 输入文件路径 |
| output | string | 否 | 输出文件路径 |
| sheet | string | 否 | 工作表名称，默认 Sheet1 |
| data | string | 否 | JSON格式的数据字符串 |
| range | string | 否 | 单元格范围，如 A1:D10 |
| headers | boolean | 否 | 是否包含表头，默认 true |
| chart_type | string | 否 | 图表类型: bar/line/pie/scatter |
| title | string | 否 | 图表标题 |
| formula | string | 否 | Excel公式 |
| cell | string | 否 | 单元格位置 |
| font | string | 否 | 字体设置(JSON) |
| fill | string | 否 | 填充设置(JSON) |
| alignment | string | 否 | 对齐设置(JSON) |

## 使用示例

### 1. 读取Excel文件

```bash
# 读取整个工作表
python main.py read --input data.xlsx --sheet Sheet1

# 读取指定范围
python main.py read --input data.xlsx --range A1:D10

# 不包含表头
python main.py read --input data.xlsx --headers false
```

### 2. 写入数据

```bash
# 写入对象数组
python main.py write --input data.xlsx --data '[{"name":"张三","age":25},{"name":"李四","age":30}]'

# 写入二维数组
python main.py write --input data.xlsx --data '[["姓名","年龄"],["张三",25],["李四",30]]'
```

### 3. 格式化单元格

```bash
# 设置背景色
python main.py format --input data.xlsx --range A1:D1 --fill '{"color":"4472C4"}'

# 设置字体
python main.py format --input data.xlsx --range A1:D10 --font '{"bold":true,"size":12}'

# 设置对齐
python main.py format --input data.xlsx --range A1:D10 --alignment '{"horizontal":"center"}'
```

### 4. 添加公式

```bash
# 求和公式
python main.py formula --input data.xlsx --cell E11 --formula "=SUM(E2:E10)"

# 平均值公式
python main.py formula --input data.xlsx --cell F11 --formula "=AVERAGE(F2:F10)"
```

### 5. 创建图表

```bash
# 柱状图
python main.py chart --input data.xlsx --chart_type bar --title "销售统计"

# 折线图
python main.py chart --input data.xlsx --chart_type line --title "趋势图"

# 饼图
python main.py chart --input data.xlsx --chart_type pie --title "占比分析"
```

### 6. 合并文件

```bash
# 垂直合并（追加）
python main.py merge --files "file1.xlsx,file2.xlsx,file3.xlsx" --output merged.xlsx
```

## 格式化选项详解

### 字体设置 (font)

```json
{
  "name": "微软雅黑",
  "size": 12,
  "bold": true,
  "italic": false,
  "color": "FF0000"
}
```

### 填充设置 (fill)

```json
{
  "color": "FFFF00",
  "type": "solid"
}
```

### 对齐设置 (alignment)

```json
{
  "horizontal": "center",
  "vertical": "center",
  "wrap_text": true
}
```

水平对齐选项: `left`, `center`, `right`
垂直对齐选项: `top`, `center`, `bottom`

## 返回值格式

### 读取操作返回

```json
[
  {"姓名": "张三", "年龄": 25, "城市": "北京"},
  {"姓名": "李四", "年龄": 30, "城市": "上海"}
]
```

## 错误处理

- 文件不存在时抛出异常
- JSON格式错误时显示友好提示
- 无效的范围格式会被拒绝

## 依赖要求

- Python 3.7+
- openpyxl >= 3.1.0

## 安装依赖

```bash
pip install -r requirements.txt
```
