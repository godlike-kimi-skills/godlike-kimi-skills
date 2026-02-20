# Wrangler Skill

Cloudflare Wrangler CLI 封装工具 - 简化 Workers 开发与部署流程。

## 简介

本 Skill 提供对 Cloudflare Wrangler CLI 的高级封装，让你可以通过统一的 Python 接口快速管理：

- **Cloudflare Workers** - 无服务器边缘函数
- **KV 存储** - 键值对数据存储
- **D1 数据库** - 边缘 SQLite 数据库
- **R2 存储** - 对象存储服务

## 前置要求

1. **Node.js** >= 16.x
2. **Wrangler CLI** - 安装命令：
   ```bash
   npm install -g wrangler
   ```
3. **登录 Cloudflare**：
   ```bash
   wrangler login
   ```
4. **Python 依赖**：
   ```bash
   pip install -r requirements.txt
   ```

## 快速开始

### 1. 初始化新项目

```bash
python main.py --action init --project my-worker
```

这将创建一个基础的 Workers 项目结构。

### 2. 配置 wrangler.toml

编辑项目根目录的 `wrangler.toml`：

```toml
name = "my-worker"
main = "src/index.js"
compatibility_date = "2024-01-01"

# 你的 Cloudflare Account ID
account_id = "your-account-id"
```

### 3. 本地开发

```bash
python main.py --action dev
```

启动本地开发服务器，支持热重载。

### 4. 部署

```bash
# 部署到生产环境
python main.py --action deploy

# 或指定环境
python main.py --action deploy --env production
```

## 完整命令参考

### Workers 操作

| 命令 | 描述 |
|------|------|
| `init` | 初始化新项目 |
| `deploy` | 部署 Worker |
| `dev` | 启动开发服务器 |
| `tail` | 查看实时日志 |
| `status` | 查看项目状态 |

### KV 存储操作

```bash
# 列出所有命名空间
python main.py --action kv --command namespace

# 列出指定命名空间的键
python main.py --action kv --command list --namespace <namespace-id>

# 获取键值
python main.py --action kv --command get --namespace <id> --key mykey

# 设置键值
python main.py --action kv --command put --namespace <id> --key mykey --value "hello"

# 从文件设置
python main.py --action kv --command put --namespace <id> --key mykey --file ./data.json

# 删除键
python main.py --action kv --command delete --namespace <id> --key mykey
```

### D1 数据库操作

```bash
# 列出所有数据库
python main.py --action d1 --command list

# 创建数据库
python main.py --action d1 --command create --namespace my-database

# 执行 SQL 查询
python main.py --action d1 --command query --namespace my-database --query "SELECT * FROM users"
```

### R2 存储桶操作

```bash
# 列出所有存储桶
python main.py --action r2 --command list

# 创建存储桶
python main.py --action r2 --command create --namespace my-bucket

# 删除存储桶
python main.py --action r2 --command delete --namespace my-bucket
```

## 高级用法

### 多环境配置

在 `wrangler.toml` 中配置多个环境：

```toml
[env.staging]
name = "my-worker-staging"
routes = [{pattern = "staging.example.com/*", zone_name = "example.com"}]

[env.production]
name = "my-worker-prod"
routes = [{pattern = "api.example.com/*", zone_name = "example.com"}]
```

部署到指定环境：

```bash
python main.py --action deploy --env staging
```

### 模拟部署（Dry Run）

测试部署配置而不实际部署：

```bash
python main.py --action deploy --dry-run
```

### 查看项目配置

```bash
python main.py --action config
```

将以高亮格式显示 `wrangler.toml` 内容。

### 查看实时日志

```bash
# 查看实时日志
python main.py --action tail

# 持续跟踪（阻塞模式）
python main.py --action tail --follow
```

## 典型工作流示例

### 场景 1：新建 API 服务

```bash
# 1. 初始化项目
python main.py --action init --project my-api

# 2. 进入项目目录
cd my-api

# 3. 编辑代码
# ... 修改 src/index.js ...

# 4. 本地测试
python main.py --action dev --port 8787

# 5. 部署
python main.py --action deploy

# 6. 监控日志
python main.py --action tail
```

### 场景 2：使用 KV 缓存数据

```bash
# 1. 首先在 Cloudflare Dashboard 创建 KV 命名空间
# 获取 namespace ID

# 2. 配置 wrangler.toml
# [[kv_namespaces]]
# binding = "CACHE"
# id = "your-namespace-id"

# 3. 在代码中使用 KV
# env.CACHE.put("key", "value")

# 4. 通过 CLI 管理 KV
python main.py --action kv --command put \
  --namespace <id> \
  --key config \
  --file ./config.json
```

### 场景 3：使用 D1 数据库

```bash
# 1. 创建数据库
python main.py --action d1 --command create --namespace my-app-db

# 2. 执行建表语句
python main.py --action d1 --command query \
  --namespace my-app-db \
  --query "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)"

# 3. 插入数据
python main.py --action d1 --command query \
  --namespace my-app-db \
  --query "INSERT INTO users (name) VALUES ('Alice')"

# 4. 查询数据
python main.py --action d1 --command query \
  --namespace my-app-db \
  --query "SELECT * FROM users"
```

## 故障排查

### Wrangler 未找到

```
错误: 未找到wrangler命令，请先安装: npm install -g wrangler
```

**解决**：
```bash
npm install -g wrangler
wrangler login
```

### 未找到 wrangler.toml

```
错误: 未找到wrangler.toml，请先运行 init 命令
```

**解决**：在项目根目录运行初始化或创建 `wrangler.toml` 文件。

### 权限错误

确保已登录：
```bash
wrangler login
```

### 部署失败

检查：
1. `account_id` 是否正确配置
2. Worker 名称是否唯一
3. 代码是否有语法错误

## 配置文件参考

### wrangler.toml 完整示例

```toml
name = "my-worker"
main = "src/index.js"
compatibility_date = "2024-01-01"
account_id = "your-account-id"

# 环境变量
[vars]
API_VERSION = "v1"
DEBUG = "false"

# KV 命名空间绑定
[[kv_namespaces]]
binding = "CACHE"
id = "xxxxx"
preview_id = "yyyyy"

# D1 数据库绑定
[[d1_databases]]
binding = "DB"
database_name = "my-db"
database_id = "xxxxx"

# R2 存储桶绑定
[[r2_buckets]]
binding = "STORAGE"
bucket_name = "my-bucket"

# 路由配置
[[routes]]
pattern = "api.example.com/*"
zone_name = "example.com"

# 构建配置
[build]
command = "npm run build"
```

## API 参考

### WranglerSkill 类

```python
from main import WranglerSkill

skill = WranglerSkill("/path/to/project")

# 部署
skill.deploy(env="production")

# KV 操作
skill.kv_list(namespace_id)
skill.kv_get(namespace_id, key)
skill.kv_put(namespace_id, key, value)
skill.kv_delete(namespace_id, key)

# D1 操作
skill.d1_list()
skill.d1_query(database, query)
skill.d1_create(name)

# R2 操作
skill.r2_list_buckets()
skill.r2_create_bucket(name)
skill.r2_delete_bucket(name)
```

## 贡献

欢迎提交 Issue 和 PR！

## 许可证

MIT License
