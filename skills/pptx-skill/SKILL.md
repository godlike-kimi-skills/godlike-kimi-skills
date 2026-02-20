# PPT处理器 Skill

PowerPoint演示文稿创建与编辑工具，支持从Markdown/JSON创建PPT、使用模板、插入图表和图片。

## 功能概述

- **创建PPT**：从Markdown、JSON或代码直接生成演示文稿
- **编辑PPT**：修改现有演示文稿的内容、样式和布局
- **模板支持**：内置多种主题模板，支持自定义模板
- **图表插入**：支持柱状图、折线图、饼图等数据可视化
- **图片处理**：自动调整图片大小、裁剪和定位
- **批量操作**：合并、拆分多个PPT文件

## 使用方法

### 通过 Kimi CLI

```bash
# 从Markdown创建PPT
kimi skill pptx-skill --action create --input presentation.md --output slides.pptx

# 使用模板创建
kimi skill pptx-skill --action create --input content.json --template business --output report.pptx

# 添加图表
kimi skill pptx-skill --action edit --input existing.pptx --charts chart_config.json --output updated.pptx
```

### 通过 Python 调用

```python
from main import PPTXSkill

skill = PPTXSkill()

# 创建新PPT
skill.create_from_markdown("content.md", "output.pptx", template="modern")

# 编辑现有PPT
skill.edit_presentation("input.pptx", "output.pptx", slides=new_slides)
```

## 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| action | string | 是 | 操作类型：create/edit/merge/split/convert/template |
| input | string | 否 | 输入文件路径 |
| output | string | 否 | 输出文件路径 |
| template | string | 否 | 模板名称或路径 |
| slides | array | 否 | 幻灯片内容数组 |
| theme | string | 否 | 主题：default/dark/light/blue/green |
| charts | object | 否 | 图表配置 |
| images | array | 否 | 图片路径数组 |
| config | object | 否 | 高级配置选项 |

## 输入格式

### Markdown 格式

```markdown
# 幻灯片1标题

- 要点1
- 要点2
- 要点3

---

# 幻灯片2标题

这是一段正文内容。

![图片描述](image.png)
```

### JSON 格式

```json
{
  "title": "演示文稿标题",
  "slides": [
    {
      "title": "幻灯片1",
      "content": ["要点1", "要点2"],
      "layout": "title_and_content"
    },
    {
      "title": "数据图表",
      "chart": {
        "type": "bar",
        "data": {
          "labels": ["A", "B", "C"],
          "values": [10, 20, 30]
        }
      }
    }
  ]
}
```

## 示例

### 示例1：创建简单PPT

```bash
kimi skill pptx-skill --action create \
  --input "# 欢迎\n\n这是第一页\n\n---\n\n# 谢谢" \
  --output welcome.pptx
```

### 示例2：使用模板和图表

```bash
kimi skill pptx-skill --action create \
  --input report.json \
  --template business \
  --theme blue \
  --output annual_report.pptx
```

### 示例3：批量插入图片

```bash
kimi skill pptx-skill --action create \
  --input album.md \
  --images "img1.jpg,img2.jpg,img3.jpg" \
  --output photo_album.pptx
```

## 内置模板

| 模板名称 | 描述 | 适用场景 |
|----------|------|----------|
| default | 默认白色主题 | 通用演示 |
| business | 商务蓝主题 | 商业报告 |
| dark | 深色主题 | 产品发布 |
| minimal | 极简风格 | 学术演讲 |
| colorful | 多彩设计 | 教育培训 |

## 注意事项

1. 图片会自动调整为适合幻灯片的大小
2. 图表数据需要有效的数值格式
3. 模板文件必须是有效的.pptx格式
4. 输出文件如果已存在会被覆盖

## 依赖安装

```bash
pip install -r requirements.txt
```

## 故障排除

**Q: 图片无法显示？**
A: 检查图片路径是否正确，支持格式：PNG, JPG, JPEG, GIF, BMP

**Q: 中文显示乱码？**
A: 确保系统安装了中文字体，或使用模板中的默认字体

**Q: 图表不显示？**
A: 检查JSON数据格式，数值必须是数字类型而非字符串
