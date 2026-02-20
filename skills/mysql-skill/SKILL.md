# MySQL Skill

MySQL/MariaDB数据库连接、查询和管理工具。支持SQL执行、表管理、数据导入导出等全面数据库操作。

**Use when working with MySQL, querying data, or when user mentions 'mysql', 'mariadb', 'mysql database'**

---

## 核心功能

### 🔌 连接管理

| 功能 | 说明 | 使用场景 |
|------|------|----------|
| **多连接支持** | 同时管理多个连接 | 多环境切换 |
| **连接池** | 自动连接池管理 | 高并发场景 |
| **SSL/TLS** | 安全加密连接 | 云数据库连接 |

### 📝 SQL操作

| 功能 | 说明 | 复杂度 |
|------|------|--------|
| **基础CRUD** | SELECT/INSERT/UPDATE/DELETE | 基础 |
| **存储过程** | CALL语句执行 | 中级 |
| **事务控制** | START TRANSACTION/COMMIT/ROLLBACK | 中级 |
| **预处理语句** | 参数化查询 | 安全必备 |

### 📊 表管理

| 功能 | 说明 | 命令 |
|------|------|------|
| **创建表** | CREATE TABLE封装 | `create-table` |
| **修改表** | ALTER TABLE操作 | `alter-table` |
| **删除表** | 安全删除确认 | `drop-table` |
| **查看表** | SHOW TABLES/DESC | `tables`, `describe` |

### 🔄 数据迁移

| 功能 | 说明 | 格式支持 |
|------|------|----------|
| **数据导出** | SELECT INTO OUTFILE封装 | CSV, JSON, SQL |
| **数据导入** | LOAD DATA封装 | CSV, JSON |
| **结构导出** | 表结构DDL导出 | SQL |
| **整库备份** | mysqldump封装 | SQL |

---

## 使用方法

### 基础查询

```bash
# 执行SQL查询
python main.py query "SELECT * FROM users LIMIT 10" --host localhost --database mydb --user root

# 使用连接字符串
python main.py query "SELECT COUNT(*) FROM orders" --connection "mysql://root:pass@localhost/mydb"

# 执行文件中的SQL
python main.py execute --file script.sql --database mydb
```

### 表管理

```bash
# 列出所有表
python main.py tables --database mydb

# 查看表结构
python main.py describe users --database mydb

# 创建新表
python main.py create-table --name products --columns "id INT PRIMARY KEY, name VARCHAR(100), price DECIMAL(10,2)"

# 安全删除表（需确认）
python main.py drop-table old_table --database mydb --confirm
```

### 数据导出

```bash
# 导出查询结果到CSV
python main.py export "SELECT * FROM users WHERE created_at > '2024-01-01'" --format csv --output recent_users.csv

# 导出整个表
python main.py export-table orders --format json --output orders.json

# 导出表结构（DDL）
python main.py export-schema users --output users_schema.sql
```

### 数据导入

```bash
# 从CSV导入（自动匹配列）
python main.py import products --source data.csv --format csv --table products

# 从JSON导入
python main.py import users --source users.json --format json --table users

# 批量导入（事务控制）
python main.py batch-import large_data.csv --table orders --batch-size 1000
```

### 备份与恢复

```bash
# 备份整个数据库
python main.py backup --database mydb --output mydb_backup.sql

# 备份指定表
python main.py backup --database mydb --tables users,orders --output tables_backup.sql

# 恢复数据库
python main.py restore --source backup.sql --database mydb_new
```

### 用户与权限

```bash
# 列出所有用户
python main.py users

# 查看用户权限
python main.py grants username

# 创建用户（简化版）
python main.py create-user --name newuser --password secret --database mydb --privileges "SELECT,INSERT,UPDATE"
```

---

## 配置说明

### 环境变量

```bash
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_DATABASE=mydb
export MYSQL_USER=root
export MYSQL_PASSWORD=secret
```

### 配置文件

创建 `~/.mysql_skill_config.json`:

```json
{
  "default_connection": {
    "host": "localhost",
    "port": 3306,
    "database": "mydb",
    "user": "root",
    "charset": "utf8mb4"
  },
  "connections": {
    "production": {
      "host": "prod.mysql.com",
      "port": 3306,
      "database": "prod_db",
      "user": "app_user",
      "ssl": true
    }
  }
}
```

---

## Out of Scope

以下功能**不在支持范围内**：

| 功能 | 原因 | 替代方案 |
|------|------|----------|
| **主从复制配置** | 架构级别操作 | 手动配置或使用Orchestrator |
| **集群管理** | 需要专业工具 | MySQL Group Replication |
| **性能调优** | 需要深度分析 | 使用MySQL Tuner, pt-query-digest |
| **安全审计** | 需要专业审计工具 | McAfee, Imperva等 |
| **数据加密(TDE)** | 存储层操作 | 配置InnoDB透明加密 |

---

## 错误处理

### 常见错误

| 错误代码 | 说明 | 解决方案 |
|----------|------|----------|
| `2003` | 无法连接 | 检查MySQL服务/防火墙 |
| `1045` | 访问被拒绝 | 检查用户名/密码/主机 |
| `1146` | 表不存在 | 检查表名/数据库 |
| `1062` | 重复键 | 检查唯一约束 |
| `1205` | 锁等待超时 | 优化事务或重试 |

### 调试模式

```bash
# 显示详细日志
python main.py query "SELECT 1" --verbose

# 显示执行计划
python main.py explain "SELECT * FROM users WHERE id = 1"
```

---

## MySQL vs MariaDB兼容性

| 特性 | MySQL | MariaDB | 支持状态 |
|------|-------|---------|----------|
| 基础SQL | ✅ | ✅ | 完全支持 |
| JSON函数 | ✅ | ✅ | 完全支持 |
| 窗口函数 | 8.0+ | 10.2+ | 版本依赖 |
| CTE | 8.0+ | 10.2+ | 版本依赖 |

---

## 最佳实践

1. **使用UTF8MB4**：始终使用utf8mb4字符集
2. **索引优化**：为常用查询条件添加索引
3. **批量操作**：大数据量使用批量导入
4. **定期备份**：使用backup功能定期备份
5. **监控慢查询**：启用slow_query_log

---

## 版本信息

- **Version**: 1.0.0
- **Author**: KbotGenesis
- **License**: MIT
- **Requirements**: PyMySQL >= 1.0.0
- **Last Updated**: 2026-02-20
