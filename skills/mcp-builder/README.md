# MCP Builder

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-1.0+-green.svg)](https://modelcontextprotocol.io)

**快速构建MCP(Model Context Protocol)服务器，集成外部API和工具到Kimi CLI**

[English](#english) | [中文](#中文)

</div>

---

<a name="中文"></a>
## 中文

### 功能特性

- 🚀 **一键生成** - 快速创建MCP服务器项目结构
- 🔌 **双传输模式** - 支持stdio和sse两种传输方式
- 📦 **丰富模板** - 内置天气、搜索、计算器等常用工具模板
- ✅ **配置验证** - 自动验证MCP服务器配置
- 🛠️ **开发友好** - 完整的开发示例和最佳实践

### 快速开始

#### 安装

```bash
git clone https://github.com/godlike-kimi-skills/mcp-builder.git
cd mcp-builder
pip install -r requirements.txt
```

#### 创建第一个MCP服务器

```bash
# 创建stdio模式服务器
python main.py init --name my-server --output ./my-mcp

# 创建SSE模式服务器
python main.py init --name api-server --transport sse --port 8080
```

#### 运行服务器

```bash
cd my-mcp
python server.py
```

### 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| action | string | 是 | init | 操作类型: init/add-tool/build/validate |
| name | string | 否 | mcp-server | 服务器名称 |
| output | string | 否 | ./mcp-server | 输出目录 |
| transport | string | 否 | stdio | 传输方式: stdio/sse |
| port | integer | 否 | 3000 | SSE模式端口 |
| templates | array | 否 | [] | 预设模板 |
| force | boolean | 否 | false | 强制覆盖 |

### 使用模板

```bash
# 单个模板
python main.py init --templates weather

# 多个模板
python main.py init --templates weather search calculator
```

可用模板：
- `weather` - 天气查询工具
- `search` - 搜索工具
- `calculator` - 计算器
- `file` - 文件操作

### 项目结构

```
my-mcp/
├── server.py          # 主服务器文件
├── config.json        # 配置文件
├── requirements.txt   # Python依赖
├── tools/             # 工具实现目录
│   ├── __init__.py
│   └── *.py          # 工具模块
└── README.md          # 项目说明
```

### 开发自定义工具

```python
# tools/my_tool.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
async def custom_tool(input: str) -> str:
    """自定义工具描述"""
    return f"结果: {input}"
```

### 配置Kimi CLI

在 `.kimi/skills/my-mcp/skill.json` 中添加：

```json
{
  "name": "my-mcp",
  "title": "我的MCP工具",
  "entry_point": "server.py",
  "transport": "stdio"
}
```

---

<a name="english"></a>
## English

### Features

- 🚀 **One-click Generation** - Quickly create MCP server project structure
- 🔌 **Dual Transport Modes** - Support for both stdio and sse transports
- 📦 **Rich Templates** - Built-in templates for weather, search, calculator and more
- ✅ **Config Validation** - Automatic validation of MCP server configuration
- 🛠️ **Developer Friendly** - Complete examples and best practices

### Quick Start

#### Installation

```bash
git clone https://github.com/godlike-kimi-skills/mcp-builder.git
cd mcp-builder
pip install -r requirements.txt
```

#### Create Your First MCP Server

```bash
# Create stdio mode server
python main.py init --name my-server --output ./my-mcp

# Create SSE mode server
python main.py init --name api-server --transport sse --port 8080
```

#### Run Server

```bash
cd my-mcp
python server.py
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| action | string | Yes | init | Action type: init/add-tool/build/validate |
| name | string | No | mcp-server | Server name |
| output | string | No | ./mcp-server | Output directory |
| transport | string | No | stdio | Transport: stdio/sse |
| port | integer | No | 3000 | Port for SSE mode |
| templates | array | No | [] | Preset templates |
| force | boolean | No | false | Force overwrite |

### Using Templates

```bash
# Single template
python main.py init --templates weather

# Multiple templates
python main.py init --templates weather search calculator
```

Available templates:
- `weather` - Weather query tools
- `search` - Search tools
- `calculator` - Calculator
- `file` - File operations

### Project Structure

```
my-mcp/
├── server.py          # Main server file
├── config.json        # Configuration
├── requirements.txt   # Python dependencies
├── tools/             # Tools directory
│   ├── __init__.py
│   └── *.py          # Tool modules
└── README.md          # Documentation
```

### Develop Custom Tools

```python
# tools/my_tool.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
async def custom_tool(input: str) -> str:
    """Custom tool description"""
    return f"Result: {input}"
```

### Configure Kimi CLI

Add to `.kimi/skills/my-mcp/skill.json`:

```json
{
  "name": "my-mcp",
  "title": "My MCP Tool",
  "entry_point": "server.py",
  "transport": "stdio"
}
```

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

欢迎提交Issue和PR！

Issues and PRs are welcome!

## Support

- 📧 Email: support@godlike-kimi-skills.dev
- 💬 Discussions: [GitHub Discussions](https://github.com/godlike-kimi-skills/mcp-builder/discussions)

---

<div align="center">

Made with ❤️ by godlike-kimi-skills

</div>
