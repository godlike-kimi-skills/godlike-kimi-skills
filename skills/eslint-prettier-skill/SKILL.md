# ESLint Prettier Skill

ESLint和Prettier配置工具，提供规则配置、自动修复、集成设置和代码风格统一功能。

## Description

ESLint和Prettier配置工具。支持规则配置、自动修复、集成设置和代码风格统一。Use when developing frontend applications, formatting code, or when user mentions 'ESLint', 'Prettier', 'lint', 'format', 'React', 'Vue'.

## Features

- **ESLint配置**：生成.eslintrc配置，支持多种预设
- **Prettier配置**：生成.prettierrc配置，统一代码风格
- **框架集成**：React、Vue、TypeScript等框架支持
- **规则管理**：自定义规则集和推荐配置
- **自动修复**：批量修复代码问题
- **忽略文件**：生成.eslintignore和.prettierignore

## Installation

```bash
# 安装依赖
pip install -r requirements.txt
```

## Usage

### 生成ESLint配置

```python
from main import ESLintGenerator

generator = ESLintGenerator()

# 生成React项目配置
config = generator.generate_config(
    framework="react",
    typescript=True,
    rules={"react/prop-types": "off"}
)
generator.save_config(config, "./.eslintrc.json")
```

### 生成Prettier配置

```python
from main import PrettierGenerator

generator = PrettierGenerator()

# 生成配置
config = generator.generate_config(
    semi=True,
    singleQuote=True,
    tabWidth=2
)
generator.save_config(config, "./.prettierrc")
```

### 命令行使用

```bash
# 生成ESLint配置
python main.py eslint --framework react --typescript

# 生成Prettier配置
python main.py prettier --semi --single-quote --tab-width 2

# 生成集成配置
python main.py integrate --framework vue --typescript

# 生成忽略文件
python main.py ignore
```

## API Reference

### ESLintGenerator

ESLint配置生成器。

#### Methods

- `generate_config(options)` - 生成ESLint配置
- `get_recommended_rules(framework)` - 获取推荐规则
- `generate_ignore_files()` - 生成忽略文件
- `validate_config(config)` - 验证配置有效性

### PrettierGenerator

Prettier配置生成器。

#### Methods

- `generate_config(options)` - 生成Prettier配置
- `get_preset(preset_name)` - 获取预设配置
- `generate_ignore_files()` - 生成忽略文件

## Examples

查看 `examples/` 目录获取更多使用示例：

- `eslint_examples.py` - ESLint配置示例
- `prettier_examples.py` - Prettier配置示例
- `integration_examples.py` - 集成配置示例

## Testing

```bash
# 运行测试
python test.py
```

## License

MIT License
