# MongoDB Skill

MongoDB文档数据库管理工具。支持文档查询、聚合管道、数据备份等NoSQL数据库操作。

**Use when working with MongoDB, querying data, or when user mentions 'mongodb', 'mongo', 'nosql database'**

---

## 核心功能

### 🔌 连接管理

| 功能 | 说明 | 使用场景 |
|------|------|----------|
| **单节点连接** | 单机MongoDB连接 | 开发/测试环境 |
| **副本集连接** | 自动故障转移 | 生产环境 |
| **分片集群** | mongos路由连接 | 大数据场景 |
| **SRV连接** | Atlas等云服务 | 云托管MongoDB |

### 🔍 文档查询

| 功能 | 说明 | 复杂度 |
|------|------|--------|
| **find查询** | 基础文档查询 | 基础 |
| **条件查询** | $eq, $gt, $in等 | 基础 |
| **正则匹配** | $regex查询 | 中级 |
| **数组查询** | $all, $elemMatch | 中级 |
| **投影选择** | 字段过滤 | 基础 |

### 🔄 聚合管道

| 阶段 | 说明 | 使用频率 |
|------|------|----------|
| **$match** | 过滤文档 | 高 |
| **$group** | 分组聚合 | 高 |
| **$sort** | 排序 | 高 |
| **$project** | 字段投影 | 高 |
| **$lookup** | 关联查询 | 中 |
| **$unwind** | 展开数组 | 中 |

### 💾 数据管理

| 功能 | 说明 | 命令 |
|------|------|------|
| **CRUD操作** | 增删改查 | `insert`, `update`, `delete` |
| **批量操作** | 批量写入 | `bulk` |
| **数据导出** | 导出JSON/CSV | `export` |
| **数据导入** | 导入JSON | `import` |
| **备份恢复** | mongodump封装 | `backup`, `restore` |

---

## 使用方法

### 连接与基础查询

```bash
# 连接本地MongoDB
python main.py find users --database mydb --limit 10

# 连接指定URI
python main.py find users --uri "mongodb://user:pass@localhost:27017/mydb"

# 连接Atlas
python main.py collections --uri "mongodb+srv://user:pass@cluster.mongodb.net/mydb"
```

### 文档查询

```bash
# 基础查询
python main.py find users --database mydb

# 条件查询
python main.py find users --database mydb --filter '{"age": {"$gte": 18}}'

# 多条件查询
python main.py find products --database shop --filter '{"category": "electronics", "price": {"$lt": 1000}}'

# 正则查询
python main.py find users --database mydb --filter '{"email": {"$regex": "@gmail.com"}}'

# 查询特定字段
python main.py find users --database mydb --fields '{"name": 1, "email": 1}'

# 排序和分页
python main.py find orders --database mydb --sort '{"created_at": -1}' --skip 10 --limit 20
```

### 聚合管道

```bash
# 基础聚合 - 统计
python main.py aggregate users --database mydb --pipeline '[{"$group": {"_id": "$status", "count": {"$sum": 1}}}]'

# 复杂聚合
python main.py aggregate orders --database mydb --pipeline '[{"$match": {"status": "completed"}}, {"$group": {"_id": "$customer_id", "total": {"$sum": "$amount"}}}, {"$sort": {"total": -1}}]'

# 关联查询（$lookup）
python main.py aggregate orders --database mydb --pipeline '[{"$lookup": {"from": "customers", "localField": "customer_id", "foreignField": "_id", "as": "customer"}}]'

# 保存聚合结果到新集合
python main.py aggregate orders --database mydb --pipeline '[{"$group": {"_id": "$month", "total": {"$sum": 1}}}]' --out monthly_stats
```

### 数据修改

```bash
# 插入文档
python main.py insert users --database mydb --doc '{"name": "John", "email": "john@example.com"}'

# 批量插入
python main.py insert-many users --database mydb --file users.json

# 更新文档
python main.py update users --database mydb --filter '{"_id": "123"}' --update '{"$set": {"name": "Jane"}}'

# 更新多个
python main.py update-many users --database mydb --filter '{"status": "pending"}' --update '{"$set": {"status": "active"}}'

# 删除文档
python main.py delete users --database mydb --filter '{"_id": "123"}'

# 删除多个
python main.py delete-many users --database mydb --filter '{"inactive": true}'
```

### 数据导出导入

```bash
# 导出集合到JSON
python main.py export users --database mydb --format json --output users.json

# 导出到CSV
python main.py export users --database mydb --format csv --output users.csv --fields name,email,age

# 从JSON导入
python main.py import users --database mydb --file users.json

# 批量导入
python main.py bulk-import orders --database mydb --file orders.json
```

### 数据库管理

```bash
# 列出所有数据库
python main.py databases

# 列出集合
python main.py collections --database mydb

# 查看集合统计
python main.py stats users --database mydb

# 创建索引
python main.py create-index users --database mydb --field email --unique

# 列出索引
python main.py indexes users --database mydb

# 删除索引
python main.py drop-index users --database mydb --name email_1
```

### 备份与恢复

```bash
# 备份数据库
python main.py backup --database mydb --output mydb_backup

# 备份指定集合
python main.py backup --database mydb --collection users --output users_backup

# 恢复数据库
python main.py restore --source mydb_backup --database mydb_new
```

---

## 配置说明

### 环境变量

```bash
export MONGODB_URI=mongodb://localhost:27017
export MONGODB_DATABASE=mydb
export MONGODB_USERNAME=user
export MONGODB_PASSWORD=secret
```

### 连接选项

| 选项 | 说明 | 示例值 |
|------|------|--------|
| `maxPoolSize` | 连接池大小 | 100 |
| `minPoolSize` | 最小连接数 | 10 |
| `maxIdleTimeMS` | 空闲超时 | 60000 |
| `retryWrites` | 写重试 | true |
| `w` | 写关注 | majority |

---

## Out of Scope

以下功能**不在支持范围内**：

| 功能 | 原因 | 替代方案 |
|------|------|----------|
| **副本集配置** | 架构级别操作 | 使用rs.reconfig() |
| **分片管理** | 集群管理操作 | mongosh或Ops Manager |
| **用户管理** | 安全敏感操作 | 使用db.createUser() |
| **GridFS** | 大文件存储 | 使用GridFS专用API |
| **变更流** | 实时监听 | 使用pymongo ChangeStream |
| **事务多文档ACID** | 复杂事务场景 | 使用原生pymongo会话 |

---

## 错误处理

### 常见错误

| 错误 | 说明 | 解决方案 |
|------|------|----------|
| `ServerSelectionTimeoutError` | 连接失败 | 检查MongoDB服务/网络 |
| `DuplicateKeyError` | 唯一键冲突 | 检查索引约束 |
| `BulkWriteError` | 批量写入错误 | 查看详细错误列表 |
| `OperationFailure` | 权限不足 | 检查用户权限 |

### 调试模式

```bash
# 显示详细日志
python main.py find users --database mydb --verbose

# 显示查询计划
python main.py explain users --database mydb --filter '{"age": 25}'
```

---

## BSON类型支持

| 类型 | 表示 | 示例 |
|------|------|------|
| ObjectId | `$oid` | `{"$oid": "..."}` |
| ISODate | `$date` | `{"$date": "2024-01-01"}` |
| NumberLong | `$numberLong` | `{"$numberLong": "123"}` |
| Binary | `$binary` | `{"$binary": "..."}` |

---

## 最佳实践

1. **使用投影**：查询时只返回需要的字段
2. **适当索引**：为查询字段创建索引
3. **批量操作**：使用批量写入提高性能
4. **限制结果**：使用limit()避免大数据量
5. **聚合优化**：在$match阶段尽早过滤数据
6. **连接池**：复用连接，不要频繁创建

---

## 版本信息

- **Version**: 1.0.0
- **Author**: KbotGenesis
- **License**: MIT
- **Requirements**: pymongo >= 4.0.0
- **Last Updated**: 2026-02-20
