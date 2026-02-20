# Vite Skill

Vite构建工具管理工具，提供项目创建、配置优化、插件管理和构建分析功能。

## Description

Vite构建工具管理工具。支持项目创建、配置优化、插件管理和构建分析。Use when developing frontend applications, building projects, or when user mentions 'Vite', 'build', 'bundler', 'React', 'Vue'.

## Features

- **项目创建**：快速生成Vite项目脚手架
- **配置优化**：vite.config.ts配置生成和优化
- **插件管理**：常用插件配置和推荐
- **构建分析**：输出分析和优化建议
- **环境配置**：开发和生产环境配置
- **代理设置**：开发服务器代理配置

## Installation

```bash
# 安装依赖
pip install -r requirements.txt
```

## Usage

### 生成配置文件

```python
from main import ViteGenerator

generator = ViteGenerator()

# 生成Vite配置
config = generator.generate_config({
    "framework": "react",
    "plugins": ["@vitejs/plugin-react"],
    "base": "/app/"
})
generator.save_config(config, "./vite.config.ts")
```

### 项目创建建议

```python
# 获取项目创建命令
commands = generator.get_project_commands("my-app", template="react-ts")
for cmd in commands:
    print(cmd)
```

### 命令行使用

```bash
# 生成配置文件
python main.py config --framework react --plugins @vitejs/plugin-react

# 生成项目结构
python main.py project my-app --template vue-ts

# 生成插件配置
python main.py plugin legacy --targets "defaults"

# 优化构建配置
python main.py optimize --analyze --compress
```

## API Reference

### ViteGenerator

主生成器类，提供所有核心功能。

#### Methods

- `generate_config(options)` - 生成Vite配置
- `generate_project(name, template)` - 生成项目结构
- `get_plugin_config(name, options)` - 获取插件配置
- `generate_env(env, vars)` - 生成环境变量文件
- `get_project_commands(name, template)` - 获取项目创建命令
- `analyze_build(output)` - 分析构建输出

### ViteTemplates

项目模板库。

#### Available Templates

- `vanilla` - 原生JavaScript
- `vanilla-ts` - 原生TypeScript
- `vue` - Vue 3
- `vue-ts` - Vue 3 + TypeScript
- `react` - React
- `react-ts` - React + TypeScript
- `react-swc` - React + SWC
- `preact` - Preact
- `lit` - Lit
- `svelte` - Svelte

## Examples

查看 `examples/` 目录获取更多使用示例：

- `config_examples.py` - 配置生成示例
- `plugin_examples.py` - 插件配置示例
- `project_examples.py` - 项目创建示例

## Testing

```bash
# 运行测试
python test.py
```

## License

MIT License
