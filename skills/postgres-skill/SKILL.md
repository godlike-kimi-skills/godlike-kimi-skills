# PostgreSQL Skill

PostgreSQL数据库连接、查询和管理工具。支持SQL执行、表结构查看、数据导入导出等核心数据库操作。

**Use when working with PostgreSQL, querying data, or when user mentions 'postgres', 'psql', 'postgresql database'**

---

## 核心功能

### 🔌 连接管理

| 功能 | 说明 | 使用场景 |
|------|------|----------|
| **连接配置** | 支持多种连接方式 | 快速连接数据库 |
| **连接池** | 内置连接池管理 | 高频查询场景 |
| **SSL支持** | 加密连接支持 | 生产环境安全连接 |

### 📝 SQL操作

| 功能 | 说明 | 复杂度 |
|------|------|--------|
| **执行查询** | 执行SELECT/INSERT/UPDATE/DELETE | 基础 |
| **批量操作** | 批量插入/更新数据 | 中级 |
| **事务管理** | BEGIN/COMMIT/ROLLBACK | 中级 |
| **参数化查询** | 防止SQL注入 | 安全必备 |

### 📊 数据管理

| 功能 | 说明 | 输出格式 |
|------|------|----------|
| **表结构查看** | DESCRIBE/\d 命令 | 结构化展示 |
| **数据导出** | 导出到CSV/JSON/SQL | 多格式支持 |
| **数据导入** | 从CSV/JSON导入 | 批量导入 |
| **备份恢复** | pg_dump/pg_restore封装 | 完整备份 |

---

## 使用方法

### 基础查询

```bash
# 执行SQL查询
python main.py query "SELECT * FROM users LIMIT 10" --host localhost --database mydb --user postgres

# 使用连接字符串
python main.py query "SELECT COUNT(*) FROM orders" --connection "postgresql://user:pass@localhost/db"
```

### 表结构查看

```bash
# 查看所有表
python main.py tables --database mydb

# 查看表结构
python main.py describe users --database mydb

# 查看索引
python main.py indexes users --database mydb
```

### 数据导出

```bash
# 导出到CSV
python main.py export "SELECT * FROM users" --format csv --output users.csv

# 导出到JSON
python main.py export "SELECT * FROM orders" --format json --output orders.json

# 导出整个表
python main.py export-table users --format csv --output users.csv
```

### 数据导入

```bash
# 从CSV导入
python main.py import users --source data.csv --format csv

# 从JSON导入
python main.py import products --source data.json --format json
```

### 备份与恢复

```bash
# 备份数据库
python main.py backup --database mydb --output backup.sql

# 备份指定表
python main.py backup --database mydb --table users --output users_backup.sql

# 恢复数据库
python main.py restore --source backup.sql --database mydb
```

---

## 配置说明

### 环境变量

```bash
export PGHOST=localhost
export PGPORT=5432
export PGDATABASE=mydb
export PGUSER=postgres
export PGPASSWORD=secret
```

### 配置文件

创建 `~/.pg_skill_config.json`:

```json
{
  "default_connection": {
    "host": "localhost",
    "port": 5432,
    "database": "mydb",
    "user": "postgres"
  },
  "connections": {
    "production": {
      "host": "prod.db.com",
      "port": 5432,
      "database": "prod_db",
      "user": "app_user",
      "sslmode": "require"
    }
  }
}
```

---

## Out of Scope

以下功能**不在支持范围内**：

| 功能 | 原因 | 替代方案 |
|------|------|----------|
| **数据库创建/删除** | 高风险操作，需DBA权限 | 使用psql命令行 |
| **用户权限管理** | 安全敏感操作 | 使用pgAdmin或psql |
| **集群管理** | 超出单个工具范围 | 使用Patroni等专业工具 |
| **性能调优** | 需要深度分析 | 使用pg_stat_statements等 |
| **复制配置** | 架构级别操作 | 手动配置流复制 |

---

## 错误处理

### 常见错误

| 错误代码 | 说明 | 解决方案 |
|----------|------|----------|
| `ConnectionError` | 连接失败 | 检查主机/端口/防火墙 |
| `AuthenticationError` | 认证失败 | 检查用户名/密码 |
| `QueryError` | SQL错误 | 检查SQL语法 |
| `TimeoutError` | 查询超时 | 优化查询或增加超时时间 |

### 日志级别

```bash
# 调试模式
python main.py query "SELECT 1" --verbose

# 静默模式
python main.py query "SELECT 1" --quiet
```

---

## 最佳实践

1. **使用参数化查询**：始终使用参数化查询防止SQL注入
2. **限制结果集**：查询时添加LIMIT避免大数据量返回
3. **使用连接池**：高频场景启用连接池
4. **定期备份**：使用backup功能定期备份重要数据
5. **监控慢查询**：关注执行时间过长的查询

---

## 版本信息

- **Version**: 1.0.0
- **Author**: KbotGenesis
- **License**: MIT
- **Requirements**: psycopg2-binary >= 2.9.0
- **Last Updated**: 2026-02-20
