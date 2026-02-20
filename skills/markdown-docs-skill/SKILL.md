# Markdown Docs Skill

Markdown文档生成工具。Use when documenting APIs, generating documentation, or when user mentions 'OpenAPI', 'Swagger', 'API docs'.

## 功能特性

- 📝 自动生成README文档
- 🔌 从OpenAPI生成API文档
- 📋 Changelog维护和管理
- 🎨 多种文档模板
- 🏗️ Markdown文档构建器

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 生成README文档

```python
from main import generate_readme

# 基础README
readme = generate_readme(
    project_name="My Awesome Project",
    description="A short description of the project.",
    template="default",
    version="1.0.0",
    author="Your Name",
    license="MIT",
    repository="https://github.com/username/repo"
)

print(readme)

# 保存到文件
with open("README.md", "w") as f:
    f.write(readme)
```

### 2. 使用Markdown构建器

```python
from main import MarkdownBuilder

# 创建构建器
builder = MarkdownBuilder(title="My Document")

# 添加内容
doc = (builder
    .add_badge("license", "MIT", "blue")
    .add_badge("version", "1.0.0", "green")
    .add_heading("Features", 2)
    .add_list([
        "Feature 1: Description",
        "Feature 2: Description",
        "Feature 3: Description"
    ])
    .add_heading("Installation", 2)
    .add_code_block("pip install my-package", "bash")
    .add_heading("Usage", 2)
    .add_paragraph("Here's how to use the package:")
    .add_code_block("""import mypackage

result = mypackage.do_something()
print(result)""", "python")
    .add_heading("API Reference", 2)
    .add_table(
        headers=["Method", "Description", "Returns"],
        rows=[
            ["do_something()", "Does something awesome", "Result"],
            ["get_data()", "Retrieves data", "Data"]
        ]
    )
    .build())

print(doc)
```

### 3. 生成API文档

```python
from main import generate_api_docs, APIEndpoint
import json

# 方法1: 从OpenAPI规范生成
with open("openapi.json") as f:
    openapi_spec = json.load(f)

api_doc = generate_api_docs(openapi_spec=openapi_spec, title="My API")

with open("API.md", "w") as f:
    f.write(api_doc)

# 方法2: 手动添加端点
from main import APIDocGenerator, APIEndpoint

generator = APIDocGenerator(title="Custom API")

endpoint = APIEndpoint(
    method="GET",
    path="/users",
    summary="List all users",
    description="Returns a paginated list of users",
    parameters=[
        {"name": "page", "in": "query", "schema": {"type": "integer"}, "required": False},
        {"name": "limit", "in": "query", "schema": {"type": "integer"}, "required": False}
    ],
    responses=[
        {"code": "200", "description": "List of users", "schema": {"type": "array"}},
        {"code": "401", "description": "Unauthorized"}
    ]
)

generator.add_endpoint(endpoint)
doc = generator.generate()
```

### 4. 生成和管理Changelog

```python
from main import ChangelogGenerator

# 创建生成器
generator = ChangelogGenerator()

# 添加版本记录
generator.add_version(
    version="1.2.0",
    changes=[
        "Added new feature X",
        "Improved performance of Y",
        "Fixed bug in Z"
    ],
    change_type="added"
)

generator.add_version(
    version="1.1.0",
    changes=[
        "Deprecated old API endpoint",
        "Updated documentation"
    ],
    change_type="changed"
)

generator.add_version(
    version="1.0.1",
    changes=[
        "Fixed critical security issue"
    ],
    change_type="security"
)

# 生成Changelog
changelog = generator.generate()

with open("CHANGELOG.md", "w") as f:
    f.write(changelog)
```

### 5. 命令行使用

```bash
# 生成README
python main.py readme --name "My Project" --description "A cool project" --template full --output README.md

# 从OpenAPI生成API文档
python main.py api --input openapi.json --output API.md

# 生成Changelog
python main.py changelog --name "My Project" --version 1.0.0 --output CHANGELOG.md
```

## API参考

### MarkdownBuilder

构建Markdown文档的核心类。

| 方法 | 描述 |
|------|------|
| `add_heading(text, level)` | 添加标题 |
| `add_paragraph(text)` | 添加段落 |
| `add_code_block(code, language)` | 添加代码块 |
| `add_list(items, ordered)` | 添加列表 |
| `add_table(headers, rows)` | 添加表格 |
| `add_blockquote(text)` | 添加引用 |
| `add_horizontal_rule()` | 添加分隔线 |
| `add_badge(label, message, color)` | 添加徽章 |
| `build()` | 构建并返回Markdown字符串 |

### READMEGenerator

| 方法 | 描述 |
|------|------|
| `set_section(name, content)` | 设置自定义章节 |
| `generate()` | 生成README内容 |

可用模板：
- `minimal`: 最简版本（描述、安装、使用）
- `default`: 默认版本（徽章、描述、安装、使用、API、贡献、许可）
- `full`: 完整版本（包含所有章节）

### APIDocGenerator

| 方法 | 描述 |
|------|------|
| `add_endpoint(endpoint)` | 添加API端点 |
| `add_model(name, schema)` | 添加数据模型 |
| `generate()` | 生成API文档 |

### ChangelogGenerator

| 方法 | 描述 |
|------|------|
| `add_entry(entry)` | 添加Changelog条目 |
| `add_version(version, changes, ...)` | 添加版本记录 |
| `generate()` | 生成Changelog |

变更类型：
- `added`: 新增功能
- `changed`: 变更
- `deprecated`: 弃用
- `removed`: 移除
- `fixed`: 修复
- `security`: 安全更新

## 示例：完整文档套件

```python
from main import (
    generate_readme, generate_api_docs, ChangelogGenerator,
    MarkdownBuilder, ProjectInfo
)
import json

project = ProjectInfo(
    name="Awesome API",
    description="A powerful API for awesome things",
    version="2.0.0",
    author="Developer Team",
    license="Apache-2.0",
    repository="https://github.com/example/awesome-api"
)

# 1. 生成README
readme = generate_readme(
    project_name=project.name,
    description=project.description,
    template="full",
    version=project.version,
    author=project.author,
    license=project.license,
    repository=project.repository
)

with open("README.md", "w") as f:
    f.write(readme)

# 2. 生成API文档（从OpenAPI）
with open("openapi.json") as f:
    spec = json.load(f)

api_doc = generate_api_docs(openapi_spec=spec, title=f"{project.name} API")

with open("API.md", "w") as f:
    f.write(api_doc)

# 3. 生成Changelog
changelog_gen = ChangelogGenerator()
changelog_gen.add_version(
    "2.0.0",
    ["Major API redesign", "Added new endpoints", "Improved documentation"],
    change_type="changed"
)
changelog_gen.add_version(
    "1.1.0",
    ["Added user authentication", "New reporting features"],
    change_type="added"
)
changelog_gen.add_version(
    "1.0.0",
    ["Initial release"],
    change_type="added"
)

with open("CHANGELOG.md", "w") as f:
    f.write(changelog_gen.generate())

# 4. 生成CONTRIBUTING指南
contributing = (MarkdownBuilder()
    .add_heading("Contributing to Awesome API", 1)
    .add_heading("Code of Conduct", 2)
    .add_paragraph("This project adheres to a code of conduct. By participating, you are expected to uphold this code.")
    .add_heading("How to Contribute", 2)
    .add_list([
        "Fork the repository",
        "Create a feature branch",
        "Make your changes",
        "Submit a pull request"
    ])
    .add_heading("Development Setup", 2)
    .add_code_block("""git clone https://github.com/example/awesome-api.git
cd awesome-api
pip install -r requirements-dev.txt""", "bash")
    .build())

with open("CONTRIBUTING.md", "w") as f:
    f.write(contributing)

print("Documentation generated successfully!")
```

## 输出示例

生成的README.md示例：

```markdown
# Awesome API

![license](https://img.shields.io/badge/license-Apache--2.0-blue)
![version](https://img.shields.io/badge/version-2.0.0-green)

## Description

A powerful API for awesome things

## Installation

```bash
pip install awesome-api
```

## Usage

```python
import awesome_api

client = awesome_api.Client()
result = client.get_data()
print(result)
```

## API Reference

See [API.md](API.md) for detailed API documentation.

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the Apache-2.0 License.
```

## 配置选项

在 `skill.json` 中配置默认选项：

```json
{
  "config": {
    "default_template": "default",
    "include_toc": true,
    "preserve_existing": true
  }
}
```

## 注意事项

1. 生成的Markdown使用GitHub Flavored Markdown
2. 徽章使用shields.io服务
3. Changelog遵循Keep a Changelog格式
4. API文档支持从OpenAPI 3.0规范生成
5. 所有路径参数使用标准路径格式

## 许可证

MIT License
