# MCP构建器 (MCP Builder)

快速构建MCP(Model Context Protocol)服务器，将外部API和工具集成到Kimi CLI。

## 功能概述

- **脚手架生成**: 一键生成MCP服务器项目结构
- **多传输支持**: 支持stdio和sse两种传输模式
- **工具模板**: 内置天气、搜索、计算器等常用工具模板
- **配置验证**: 验证MCP服务器配置的合法性
- **快速开发**: 提供完整的开发示例和最佳实践

## 使用方法

### 1. 初始化MCP服务器

```bash
# 基础用法 - 创建stdio模式服务器
python main.py init --name my-server --output ./my-mcp

# 创建SSE模式服务器
python main.py init --name api-server --transport sse --port 8080

# 使用预设模板
python main.py init --name weather-server --templates weather

# 多个模板组合
python main.py init --name toolkit --templates weather search calculator
```

### 2. 添加工具到现有服务器

```bash
python main.py add-tool --output ./my-mcp --name fetch-data --description "获取数据"
```

### 3. 验证配置

```bash
python main.py validate --output ./my-mcp
```

## 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| action | string | 是 | init | 操作类型: init/add-tool/build/validate |
| name | string | 否 | mcp-server | 服务器名称 |
| output | string | 否 | ./mcp-server | 输出目录 |
| transport | string | 否 | stdio | 传输方式: stdio/sse |
| port | integer | 否 | 3000 | SSE模式端口 |
| templates | array | 否 | [] | 预设模板 |
| force | boolean | 否 | false | 强制覆盖 |

## 传输模式对比

| 特性 | stdio | sse |
|------|-------|-----|
| 适用场景 | 本地工具、命令行程序 | 网络服务、远程API |
| 性能 | 低延迟 | 支持并发 |
| 部署 | 简单 | 需要网络配置 |
| 安全性 | 进程隔离 | 需要额外认证 |

## 预设模板

### weather - 天气查询
- `get_current_weather`: 获取当前天气
- `get_forecast`: 获取天气预报

### search - 搜索工具
- `web_search`: 网页搜索
- `local_search`: 本地文件搜索

### calculator - 计算器
- `calculate`: 基础计算
- `convert_unit`: 单位转换

### file - 文件操作
- `read_file`: 读取文件
- `write_file`: 写入文件
- `list_directory`: 列出目录

## 项目结构

```
my-mcp/
├── server.py          # 主服务器文件
├── config.json        # 配置文件
├── requirements.txt   # 依赖
├── tools/             # 工具实现
│   ├── __init__.py
│   └── example.py
└── README.md          # 项目说明
```

## 开发示例

### 创建自定义工具

```python
# tools/my_tool.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
async def my_custom_tool(param: str) -> str:
    """
    我的自定义工具
    
    Args:
        param: 输入参数
    
    Returns:
        处理结果
    """
    return f"处理结果: {param}"
```

### 运行服务器

```bash
# stdio模式
python server.py

# sse模式
python server.py --transport sse --port 8080
```

## 配置Kimi CLI

在 `.kimi/skills/my-mcp/skill.json` 中配置：

```json
{
  "name": "my-mcp",
  "title": "我的MCP工具",
  "entry_point": "server.py",
  "transport": "stdio"
}
```

## 最佳实践

1. **工具命名**: 使用小写字母和下划线，如 `fetch_web_page`
2. **参数设计**: 提供清晰的参数描述和默认值
3. **错误处理**: 返回友好的错误信息
4. **文档完善**: 为每个工具编写详细的docstring
5. **测试覆盖**: 为工具编写单元测试

## 故障排除

### 端口被占用
```bash
# 查找占用端口的进程
lsof -i :8080
# 或更换端口
python main.py init --port 8081
```

### 依赖安装失败
```bash
# 使用虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### stdio模式无响应
- 检查标准输入是否正确连接
- 确认没有print调试语句干扰JSON通信

## 参考链接

- [MCP官方文档](https://modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Kimi CLI文档](https://kimi.moonshot.cn)
