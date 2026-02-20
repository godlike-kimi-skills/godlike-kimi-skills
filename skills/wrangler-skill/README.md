# Wrangler Skill

<div align="center">

**🇨🇳 简体中文** | **🇺🇸 English**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Wrangler](https://img.shields.io/badge/Wrangler-CLI-orange.svg)](https://developers.cloudflare.com/workers/wrangler/)

*A Python wrapper for Cloudflare Wrangler CLI - Simplify Workers Development & Deployment*

</div>

---

## 📖 Table of Contents / 目录

- [Overview / 概述](#overview--概述)
- [Features / 特性](#features--特性)
- [Installation / 安装](#installation--安装)
- [Quick Start / 快速开始](#quick-start--快速开始)
- [Usage / 使用](#usage--使用)
- [API Reference / API 参考](#api-reference--api-参考)
- [Examples / 示例](#examples--示例)
- [Contributing / 贡献](#contributing--贡献)
- [License / 许可证](#license--许可证)

---

## Overview / 概述

**English:**

Wrangler Skill is a Python wrapper for Cloudflare Wrangler CLI, designed to simplify the development and deployment workflow of Cloudflare Workers. It provides a unified interface for managing Workers, KV storage, D1 databases, and R2 object storage.

**中文：**

Wrangler Skill 是 Cloudflare Wrangler CLI 的 Python 封装工具，旨在简化 Cloudflare Workers 的开发与部署流程。它提供统一的接口来管理 Workers、KV 存储、D1 数据库和 R2 对象存储。

---

## Features / 特性

| Feature | Description | 描述 |
|---------|-------------|------|
| 🚀 **Deploy** | One-click Workers deployment | 一键部署 Workers |
| 🔧 **Dev Server** | Local development with hot reload | 本地开发，支持热重载 |
| 📝 **KV Store** | Manage key-value pairs easily | 轻松管理键值对存储 |
| 🗄️ **D1 Database** | SQLite at the edge | 边缘 SQLite 数据库 |
| 📦 **R2 Storage** | Object storage management | 对象存储管理 |
| 📊 **Logs** | Real-time log streaming | 实时日志流 |
| ⚙️ **Config** | TOML/YAML configuration support | TOML/YAML 配置支持 |

---

## Installation / 安装

**Prerequisites / 前置要求：**

- Python >= 3.8
- Node.js >= 16.x
- Wrangler CLI (`npm install -g wrangler`)

**English:**

```bash
# Clone the repository
git clone https://github.com/your-username/wrangler-skill.git
cd wrangler-skill

# Install Python dependencies
pip install -r requirements.txt

# Login to Cloudflare
wrangler login
```

**中文：**

```bash
# 克隆仓库
git clone https://github.com/your-username/wrangler-skill.git
cd wrangler-skill

# 安装 Python 依赖
pip install -r requirements.txt

# 登录 Cloudflare
wrangler login
```

---

## Quick Start / 快速开始

**English:**

```bash
# 1. Initialize a new project
python main.py --action init --project my-worker

# 2. Navigate to project
cd my-worker

# 3. Start development server
python main.py --action dev

# 4. Deploy to production
python main.py --action deploy
```

**中文：**

```bash
# 1. 初始化新项目
python main.py --action init --project my-worker

# 2. 进入项目目录
cd my-worker

# 3. 启动开发服务器
python main.py --action dev

# 4. 部署到生产环境
python main.py --action deploy
```

---

## Usage / 使用

### Workers / 工作器

```bash
# Initialize / 初始化
python main.py --action init --project my-worker

# Deploy / 部署
python main.py --action deploy
python main.py --action deploy --env production

# Dev server / 开发服务器
python main.py --action dev
python main.py --action dev --port 8787

# View logs / 查看日志
python main.py --action tail
python main.py --action tail --follow
```

### KV Store / KV 存储

```bash
# List namespaces / 列出命名空间
python main.py --action kv --command namespace

# List keys / 列出键
python main.py --action kv --command list --namespace <namespace-id>

# Get value / 获取值
python main.py --action kv --command get --namespace <id> --key mykey

# Put value / 设置值
python main.py --action kv --command put --namespace <id> --key mykey --value "hello"

# Delete key / 删除键
python main.py --action kv --command delete --namespace <id> --key mykey
```

### D1 Database / D1 数据库

```bash
# List databases / 列出数据库
python main.py --action d1 --command list

# Create database / 创建数据库
python main.py --action d1 --command create --namespace my-db

# Execute query / 执行查询
python main.py --action d1 --command query \
  --namespace my-db \
  --query "SELECT * FROM users"
```

### R2 Storage / R2 存储

```bash
# List buckets / 列出存储桶
python main.py --action r2 --command list

# Create bucket / 创建存储桶
python main.py --action r2 --command create --namespace my-bucket

# Delete bucket / 删除存储桶
python main.py --action r2 --command delete --namespace my-bucket
```

---

## API Reference / API 参考

### WranglerSkill Class

```python
from main import WranglerSkill

# Initialize / 初始化
skill = WranglerSkill("/path/to/project")

# Deploy / 部署
skill.deploy(env="production", dry_run=False)

# KV Operations / KV 操作
skill.kv_list(namespace_id: str) -> bool
skill.kv_get(namespace_id: str, key: str) -> bool
skill.kv_put(namespace_id: str, key: str, value: str) -> bool
skill.kv_delete(namespace_id: str, key: str) -> bool

# D1 Operations / D1 操作
skill.d1_list() -> bool
skill.d1_query(database: str, query: str) -> bool
skill.d1_create(name: str) -> bool

# R2 Operations / R2 操作
skill.r2_list_buckets() -> bool
skill.r2_create_bucket(name: str) -> bool
skill.r2_delete_bucket(name: str) -> bool
```

---

## Examples / 示例

### Complete Workflow / 完整工作流

```bash
# 1. Create project / 创建项目
python main.py --action init --project my-api
cd my-api

# 2. Edit code / 编辑代码
# Edit src/index.js

# 3. Configure wrangler.toml / 配置
# Add account_id, bindings, etc.

# 4. Local test / 本地测试
python main.py --action dev

# 5. Dry run / 模拟部署
python main.py --action deploy --dry-run

# 6. Deploy / 正式部署
python main.py --action deploy --env production

# 7. Monitor / 监控
python main.py --action tail --follow
```

### Multi-environment Setup / 多环境配置

```toml
# wrangler.toml
name = "my-worker"
main = "src/index.js"
compatibility_date = "2024-01-01"

[env.staging]
name = "my-worker-staging"

[env.production]
name = "my-worker-prod"
routes = [{pattern = "api.example.com/*", zone_name = "example.com"}]
```

Deploy / 部署：

```bash
python main.py --action deploy --env staging
python main.py --action deploy --env production
```

---

## Project Structure / 项目结构

```
wrangler-skill/
├── main.py              # Main entry / 主入口
├── skill.json           # Skill config / Skill 配置
├── SKILL.md             # Detailed docs / 详细文档
├── README.md            # This file / 本文件
├── requirements.txt     # Dependencies / 依赖
├── tests/
│   └── test_basic.py    # Tests / 测试
└── LICENSE              # MIT License / MIT 许可证
```

---

## Contributing / 贡献

**English:**

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**中文：**

欢迎贡献！请随时提交 Pull Request。

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m '添加某个特性'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开 Pull Request

---

## License / 许可证

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

本项目采用 MIT 许可证 - 详情请查看 [LICENSE](LICENSE) 文件。

---

<div align="center">

**Made with ❤️ for Cloudflare Workers developers**

**为 Cloudflare Workers 开发者精心制作**

</div>
