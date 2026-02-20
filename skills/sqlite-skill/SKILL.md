# SQLite Skill

SQLite本地数据库管理工具。支持数据库创建、SQL查询、数据备份等轻量级数据库操作。

**Use when working with SQLite, querying data, or when user mentions 'sqlite', 'sqlite3', 'local database'**

---

## 核心功能

### 📁 数据库管理

| 功能 | 说明 | 使用场景 |
|------|------|----------|
| **创建数据库** | 新建.db文件 | 新项目初始化 |
| **连接管理** | 内存/文件数据库 | 测试/生产环境 |
| **数据库信息** | 查看元数据 | 数据库分析 |

### 🔍 查询分析

| 功能 | 说明 | 特点 |
|------|------|------|
| **SQL执行** | 任意SQL语句 | 完整SQLite支持 |
| **EXPLAIN** | 查询计划分析 | 性能优化 |
| **PRAGMA** | SQLite专用命令 | 数据库配置 |
| **多结果集** | 支持多SELECT | 批量查询 |

### 💾 数据操作

| 功能 | 说明 | 格式 |
|------|------|------|
| **CSV导入** | 从CSV加载数据 | CSV文件 |
| **CSV导出** | 导出表到CSV | CSV文件 |
| **JSON导出** | 导出为JSON | JSON文件 |
| **SQL导出** | 导出为SQL语句 | SQL文件 |

### 🔒 备份维护

| 功能 | 说明 | 命令 |
|------|------|------|
| **在线备份** | 不锁定数据库 | `backup` |
| **VACUUM** | 数据库优化 | `vacuum` |
| **完整性检查** | PRAGMA integrity_check | `check` |
| **大小分析** | 表大小统计 | `analyze` |

---

## 使用方法

### 数据库连接

```bash
# 连接文件数据库
python main.py query "SELECT * FROM users" --database app.db

# 创建内存数据库（临时）
python main.py query "CREATE TABLE test (id INT)" --memory

# 查看数据库信息
python main.py info --database app.db
```

### 表操作

```bash
# 列出所有表
python main.py tables --database app.db

# 查看表结构
python main.py schema users --database app.db

# 查看索引
python main.py indexes users --database app.db

# 查看创建语句
python main.py ddl users --database app.db
```

### 数据查询

```bash
# 基础查询
python main.py query "SELECT * FROM products WHERE price > 100" --database shop.db

# 格式化输出
python main.py query "SELECT * FROM users" --format table --database app.db

# 导出CSV
python main.py query "SELECT * FROM orders" --format csv --output orders.csv --database app.db

# 分析查询计划
python main.py explain "SELECT * FROM users WHERE email = 'test@example.com'" --database app.db
```

### 数据导入导出

```bash
# 从CSV导入（自动创建表）
python main.py import data.csv --table users --database app.db

# 从CSV导入到现有表
python main.py import data.csv --table users --database app.db --mode append

# 导出表到CSV
python main.py export users --format csv --output users.csv --database app.db

# 导出表到JSON
python main.py export products --format json --output products.json --database app.db

# 导出为SQL INSERT语句
python main.py export orders --format sql --output orders.sql --database app.db
```

### 数据库维护

```bash
# 备份数据库
python main.py backup app.db --output app_backup.db

# 优化数据库（VACUUM）
python main.py vacuum --database app.db

# 完整性检查
python main.py check --database app.db

# 分析表统计
python main.py analyze --database app.db
```

### PRAGMA命令

```bash
# 查看数据库版本
python main.py pragma "user_version" --database app.db

# 设置数据库版本
python main.py pragma "user_version = 2" --database app.db

# 查看表信息
python main.py pragma "table_info(users)" --database app.db

# 外键检查状态
python main.py pragma "foreign_keys" --database app.db
```

---

## 配置说明

### 默认设置

```python
# 自动提交模式
autocommit = True

# 超时设置（秒）
timeout = 5.0

# 返回行工厂
row_factory = sqlite3.Row
```

### 连接选项

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `timeout` | 锁等待超时 | 5.0 |
| `isolation_level` | 事务隔离级别 | None |
| `detect_types` | 类型检测 | 0 |
| `check_same_thread` | 线程检查 | False |

---

## Out of Scope

以下功能**不在支持范围内**：

| 功能 | 原因 | 替代方案 |
|------|------|----------|
| **加密数据库** | 需要SQLCipher扩展 | 使用sqlcipher-cli |
| **FTS全文搜索** | 需FTS扩展 | 使用fts5扩展SQL |
| **R-Tree空间索引** | 特殊扩展 | 原生SQL实现 |
| **自定义函数** | 需要Python注册 | 直接使用sqlite3模块 |
| **虚拟表** | 需自定义实现 | 使用fts5, json1等 |

---

## 错误处理

### 常见错误

| 错误 | 说明 | 解决方案 |
|------|------|----------|
| `OperationalError` | 数据库锁定 | 等待其他进程完成 |
| `IntegrityError` | 约束冲突 | 检查唯一/外键约束 |
| `DatabaseError` | 数据库损坏 | 尝试恢复或从备份还原 |
| `SyntaxError` | SQL语法错误 | 检查SQL语句 |

### 调试模式

```bash
# 显示详细错误
python main.py query "SELECT * FROM invalid_table" --verbose --database app.db

# 显示执行计划
python main.py explain "SELECT * FROM users" --database app.db
```

---

## SQLite特性支持

### 支持的扩展

| 扩展 | 功能 | 状态 |
|------|------|------|
| **json1** | JSON处理 | ✅ 内置支持 |
| **fts5** | 全文搜索 | ✅ 内置支持 |
| **rtree** | 空间索引 | ✅ 内置支持 |
| **math** | 数学函数 | ✅ 内置支持 |

### JSON操作示例

```bash
# 存储JSON
python main.py query "INSERT INTO data VALUES (1, json('{""name"": ""test""}'))" --database app.db

# 查询JSON
python main.py query "SELECT json_extract(data, '$.name') FROM records" --database app.db
```

---

## 最佳实践

1. **使用事务**：批量操作使用事务提高性能
2. **定期VACUUM**：定期执行VACUUM回收空间
3. **适当索引**：为频繁查询列添加索引
4. **WAL模式**：并发场景使用WAL模式
5. **备份策略**：定期使用backup命令备份

---

## 版本信息

- **Version**: 1.0.0
- **Author**: KbotGenesis
- **License**: MIT
- **Requirements**: Python >= 3.8 (内置sqlite3)
- **Last Updated**: 2026-02-20
