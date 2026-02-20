# poetry-skill

Poetry依赖管理Skill，提供项目初始化、依赖管理和发布打包功能。

## Use When

- 需要初始化新的Python项目结构
- 需要管理项目依赖（添加/删除/更新）
- 需要处理虚拟环境
- 需要构建和发布包到PyPI
- 需要管理项目的Python版本要求
- 需要锁定依赖版本
- 需要生成项目元数据
- 需要迁移项目到Poetry

## Out of Scope

- 不替代Poetry CLI的所有功能（只提供常见用例）
- 不处理非Python项目
- 不提供私有PyPI服务器的完整管理
- 不处理Docker容器内的Poetry配置
- 不替代版本控制系统（Git等）
- 不提供代码质量检查（这是其他工具的工作）

## Installation

```bash
pip install poetry
# 或
pipx install poetry
```

## Quick Start

### 初始化项目

```python
from poetry_skill import PoetrySkill

skill = PoetrySkill()

# 创建新项目
skill.init_project("my-awesome-project", {
    "description": "An awesome project",
    "author": "Your Name <you@example.com>",
    "python": "^3.10"
})
```

### 管理依赖

```python
# 添加依赖
skill.add_dependency("requests", "^2.28.0")
skill.add_dependency("pytest", "^7.0", dev=True)

# 安装依赖
skill.install()

# 更新依赖
skill.update("requests")
```

### 构建和发布

```python
# 构建包
skill.build()

# 发布到PyPI
skill.publish(username="your_username", password="your_password")
```

## Features

### 1. 项目初始化
- 标准项目结构创建
- pyproject.toml配置
- 虚拟环境设置
- 初始文件生成

### 2. 依赖管理
- 添加/删除依赖
- 开发依赖管理
- 依赖锁定
- 依赖解析

### 3. 虚拟环境
- 环境创建/删除
- Python版本管理
- 环境信息显示
- 环境路径管理

### 4. 构建发布
- 包构建（wheel/sdist）
- PyPI发布
- 版本管理
- 构建验证

## API Reference

### PoetrySkill

主类，提供Poetry相关功能。

#### Methods

- `init_project(name, **options)` - 初始化新项目
- `add_dependency(package, version=None, **options)` - 添加依赖
- `remove_dependency(package, **options)` - 删除依赖
- `install(**options)` - 安装依赖
- `update(package=None, **options)` - 更新依赖
- `build(**options)` - 构建包
- `publish(**options)` - 发布到PyPI
- `get_project_info()` - 获取项目信息
- `manage_venv(action, **options)` - 管理虚拟环境
- `export_requirements(output_path, **options)` - 导出requirements.txt

## Configuration

### pyproject.toml 结构

```toml
[tool.poetry]
name = "my-project"
version = "0.1.0"
description = "Project description"
authors = ["Your Name <you@example.com>"]
readme = "README.md"
license = "MIT"
homepage = "https://example.com"
repository = "https://github.com/user/repo"
keywords = ["python", "poetry"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
]

[tool.poetry.dependencies]
python = "^3.10"
requests = "^2.28.0"
click = "^8.0.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"
black = "^22.0.0"
mypy = "^1.0.0"

[tool.poetry.scripts]
my-cli = "my_package.cli:main"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

### Poetry配置选项

| 选项 | 说明 | 示例 |
|------|------|------|
| `virtualenvs.create` | 自动创建虚拟环境 | true |
| `virtualenvs.in-project` | 在项目目录创建 | true |
| `repositories.pypi` | PyPI仓库配置 | - |
| `http-basic.pypi` | PyPI认证 | username/password |

## Examples

### 示例1: 完整项目初始化

```python
skill = PoetrySkill()

# 创建项目
skill.init_project("data-processor", {
    "description": "Process data efficiently",
    "author": "Data Team <data@company.com>",
    "python": "^3.10",
    "license": "Apache-2.0"
})

# 添加核心依赖
skill.add_dependency("pandas", "^1.5.0")
skill.add_dependency("numpy", "^1.23.0")

# 添加开发依赖
skill.add_dependency("pytest", "^7.0", dev=True)
skill.add_dependency("black", "^22.0", dev=True)

# 安装
skill.install()

# 创建README
skill.generate_readme()
```

### 示例2: 依赖管理

```python
skill = PoetrySkill()

# 查看当前依赖
info = skill.get_project_info()
print(f"项目: {info['name']}")
print(f"依赖数量: {len(info['dependencies'])}")

# 更新所有依赖
skill.update()

# 移除旧依赖
skill.remove_dependency("old-package")

# 锁定依赖版本
skill.lock()
```

### 示例3: 多环境配置

```python
skill = PoetrySkill()

# 添加不同环境依赖
skill.add_dependency("pytest", "^7.0", group="test")
skill.add_dependency("sphinx", "^5.0", group="docs")
skill.add_dependency("mypy", "^1.0", group="dev")

# 只安装生产依赖
skill.install(without=["dev", "test", "docs"])

# 安装包含测试依赖
skill.install(with_groups=["test"])
```

### 示例4: 发布流程

```python
skill = PoetrySkill()

# 检查项目
info = skill.get_project_info()
print(f"发布版本: {info['version']}")

# 运行测试（假设使用pytest-skill）
# ...

# 构建
skill.build()

# 验证构建
assert skill.validate_build()

# 发布（使用token更安全）
skill.publish(token="pypi-token")
```

## Best Practices

1. **版本管理**: 使用语义化版本（Semantic Versioning）
2. **锁定文件**: 提交poetry.lock到版本控制
3. **虚拟环境**: 启用`virtualenvs.in-project`便于IDE检测
4. **分组依赖**: 使用依赖分组管理不同环境
5. **构建验证**: 发布前本地验证构建

## Troubleshooting

### 常见问题

**Q: 依赖解析冲突**
A: 尝试更新poetry或使用`--no-interaction`标志

**Q: 虚拟环境找不到**
A: 检查`poetry config virtualenvs.path`设置

**Q: PyPI发布失败**
A: 验证`~/.pypirc`配置或使用token认证

**Q: 依赖安装慢**
A: 配置国内镜像源，如Tsinghua源

## License

MIT License
