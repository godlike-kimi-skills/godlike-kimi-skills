# Tailwind CSS Skill

Tailwind CSS样式生成与管理工具，提供智能类名生成、响应式设计支持和自定义配置管理。

## Description

Tailwind CSS样式生成与管理工具。支持类名生成、响应式设计、自定义配置和智能提示。Use when developing frontend applications, styling components, or when user mentions 'Tailwind', 'CSS', 'React', 'Vue'.

## Features

- **类名生成**：根据组件需求生成最佳Tailwind类名组合
- **响应式设计**：自动生成移动端优先的响应式类名
- **自定义配置**：生成和管理tailwind.config.js配置
- **智能提示**：提供常用模式和最佳实践建议
- **颜色系统**：完整的Tailwind颜色工具
- **间距工具**：边距、填充和尺寸计算

## Installation

```bash
# 安装依赖
pip install -r requirements.txt
```

## Usage

### 生成组件样式

```python
from main import TailwindGenerator

generator = TailwindGenerator()

# 生成按钮样式
button_classes = generator.generate_component(
    component_type="button",
    variant="primary",
    size="md"
)
print(button_classes)
# 输出: "bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
```

### 生成响应式布局

```python
# 生成响应式网格
grid_classes = generator.generate_responsive({
    "mobile": "grid-cols-1",
    "tablet": "md:grid-cols-2",
    "desktop": "lg:grid-cols-4"
})
print(grid_classes)
# 输出: "grid-cols-1 md:grid-cols-2 lg:grid-cols-4"
```

### 生成配置文件

```python
# 生成tailwind.config.js
config = generator.generate_config({
    "colors": {
        "primary": "#3B82F6",
        "secondary": "#10B981"
    },
    "fonts": ["Inter", "sans-serif"]
})
generator.save_config(config, "./tailwind.config.js")
```

### 命令行使用

```bash
# 生成组件类名
python main.py component button primary md

# 生成响应式类名
python main.py responsive "grid-cols-1" "md:grid-cols-2" "lg:grid-cols-4"

# 生成配置文件
python main.py config --colors primary:#3B82F6,secondary:#10B981
```

## API Reference

### TailwindGenerator

主生成器类，提供所有核心功能。

#### Methods

- `generate_component(type, variant, size, options)` - 生成组件类名
- `generate_responsive(breakpoints)` - 生成响应式类名
- `generate_config(options)` - 生成配置文件
- `generate_spacing(size, type)` - 生成间距类名
- `generate_color(base, shade, opacity)` - 生成颜色类名
- `validate_classes(classes)` - 验证类名有效性
- `optimize_classes(classes)` - 优化和去重类名

### ComponentPresets

预设组件样式库。

#### Available Components

- `button` - 按钮组件（primary, secondary, danger, ghost）
- `card` - 卡片组件（default, outlined, elevated）
- `input` - 输入框组件（default, error, success）
- `badge` - 标签组件（default, primary, success, warning, danger）
- `alert` - 警告框组件（info, success, warning, error）

## Examples

查看 `examples/` 目录获取更多使用示例：

- `component_examples.py` - 组件生成示例
- `responsive_examples.py` - 响应式设计示例
- `config_examples.py` - 配置生成示例

## Testing

```bash
# 运行测试
python test.py
```

## License

MIT License
