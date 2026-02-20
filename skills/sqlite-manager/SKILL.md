# SQLite Manager

**SQLite 数据库管理工具** - 轻量级、高性能、嵌入式数据库解决方案

数据库设计、查询优化、性能调优、备份恢复，适用于本地应用和边缘计算场景。

---

## 核心特性

### 📊 适用场景

| 场景 | 优势 | 限制 |
|------|------|------|
| **移动应用** | 零配置、轻量级 | 无多客户端并发 |
| **桌面应用** | 文件存储、便携 | 不适合高并发写入 |
| **数据分析** | 快速原型、SQL支持 | 大数据量性能下降 |
| **缓存层** | 本地缓存、离线优先 | 无内置过期机制 |
| **IoT/边缘** | 资源占用低 | 需要文件系统 |

### 🔧 核心功能

```
功能矩阵:
├── DDL 管理 (创建/修改/删除表)
├── DML 操作 (CRUD)
├── 索引优化
├── 事务管理
├── 备份恢复
├── 数据导入导出
├── 查询分析
└── 性能监控
```

---

## 使用方法

### CLI 命令

```bash
# 创建数据库
sqlite-manager create myapp.db

# 执行 SQL 文件
sqlite-manager exec myapp.db --file schema.sql

# 交互式查询
sqlite-manager query myapp.db "SELECT * FROM users LIMIT 10"

# 导出数据
sqlite-manager export myapp.db --table users --format csv --output users.csv

# 导入数据
sqlite-manager import myapp.db --file data.csv --table users --create

# 备份数据库
sqlite-manager backup myapp.db --output myapp_backup_$(date +%Y%m%d).db

# 优化数据库
sqlite-manager optimize myapp.db --vacuum --analyze

# 查看表结构
sqlite-manager schema myapp.db --table users

# 性能分析
sqlite-manager analyze myapp.db --query "SELECT * FROM users WHERE email = ?"
```

### Python API

```python
from sqlite_manager import Database

# 连接数据库
db = Database('myapp.db')

# 创建表
db.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# 插入数据
db.insert('users', {
    'email': 'user@example.com',
    'name': 'John Doe'
})

# 查询数据
users = db.query('SELECT * FROM users WHERE name LIKE ?', ['%John%'])

# 事务处理
with db.transaction():
    db.insert('orders', {...})
    db.update('inventory', {...}, 'id = ?', [item_id])

# 关闭连接
db.close()
```

---

## 高级功能

### 索引优化

```sql
-- 单列索引
CREATE INDEX idx_users_email ON users(email);

-- 复合索引
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at);

-- 部分索引
CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';

-- 覆盖索引
CREATE INDEX idx_covering ON orders(user_id, status, total) 
WHERE status = 'pending';
```

### 查询优化

```python
# 使用 EXPLAIN QUERY PLAN
analysis = db.analyze('''
    SELECT u.name, COUNT(o.id) as order_count
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    WHERE u.created_at > '2024-01-01'
    GROUP BY u.id
''')

# 输出优化建议
print(analysis.recommendations)
```

### 批量操作

```python
# 高效批量插入
users = [
    {'email': 'a@example.com', 'name': 'A'},
    {'email': 'b@example.com', 'name': 'B'},
    # ... 大量数据
]

# 使用事务包裹批量操作
with db.transaction():
    db.executemany('INSERT INTO users (email, name) VALUES (?, ?)', 
                   [(u['email'], u['name']) for u in users])
```

---

## 性能优化

### PRAGMA 配置

```sql
-- 性能优化设置
PRAGMA journal_mode = WAL;          -- 写前日志模式
PRAGMA synchronous = NORMAL;        -- 同步模式
PRAGMA cache_size = 10000;          -- 缓存页数
PRAGMA temp_store = MEMORY;         -- 临时表存储
PRAGMA mmap_size = 30000000000;     -- 内存映射大小
```

### 性能基准

| 操作 | 性能指标 | 优化建议 |
|------|----------|----------|
| 单条插入 | ~1000 tx/s | 批量插入 |
| 批量插入 | ~50K-100K rows/s | 事务包裹 |
| 简单查询 | < 1ms | 索引覆盖 |
| 复杂 JOIN | 10-100ms | 优化查询 |
| 数据库大小 | 适合 < 1TB | 分区归档 |

---

## 数据迁移

### 版本控制

```python
# 迁移脚本管理
from sqlite_manager import Migration

migration = Migration(db)

# 创建迁移
migration.create('add_user_profile', '''
    ALTER TABLE users ADD COLUMN profile JSON;
''')

# 执行迁移
migration.up()

# 回滚
migration.down()
```

### 数据导出

```bash
# 全库导出
sqlite-manager dump myapp.db --output backup.sql

# 特定表导出
sqlite-manager export myapp.db --table users --format json --pretty

# 压缩导出
sqlite-manager backup myapp.db --compress --output myapp.db.gz
```

---

## 最佳实践

### 设计原则

```
1. 规范化
   - 第三范式为主
   - 适度反规范化优化查询
   
2. 索引策略
   - 主键自动索引
   - 外键创建索引
   - 查询条件列索引
   - 避免过多索引影响写入
   
3. 事务使用
   - 批量操作使用事务
   - 保持事务简短
   - 避免长时间锁定
   
4. 连接管理
   - 使用连接池
   - 及时关闭连接
   - WAL 模式提升并发
```

### 安全建议

```python
# ✅ 参数化查询 (防 SQL 注入)
db.query('SELECT * FROM users WHERE email = ?', [user_email])

# ❌ 避免字符串拼接
db.query(f'SELECT * FROM users WHERE email = "{user_email}"')  # 危险!
```

---

## 质量保障体系

基于PDCA循环、精益思想、约束理论、六西格玛和持续改进框架，建立生产级数据库质量保障体系。

### 质量目标 (SLA)

| 指标 | 目标值 | 测量方法 |
|-----|--------|---------|
| 查询响应时间 | P95 < 10ms | 查询性能监控 |
| 数据完整性 | 事务成功率 >99.99% | 事务日志分析 |
| 备份成功率 | 100% | 备份任务监控 |
| 恢复时间 (RTO) | < 1小时 | 恢复演练 |
| 数据丢失 (RPO) | < 5分钟 | 备份策略验证 |
| 数据库可用性 | >99.9% | 健康检查 |

### PDCA质量循环

```
Plan (计划)
├── 容量规划 (数据量/并发/增长预测)
├── Schema设计与审查
├── 索引策略规划
├── 备份策略制定
└── 性能目标定义
        ↓
Do (执行)
├── 开发环境验证
├── 测试环境压测
├── 渐进式部署
├── 监控数据采集
└── 文档记录
        ↓
Check (检查)
├── 性能基准对比
├── 查询计划分析
├── 健康状态检查
├── 备份验证
└── 容量趋势分析
        ↓
Act (处理)
├── 查询优化
├── Schema调整
├── 配置优化
├── 流程标准化
└── 知识沉淀
```

### 容量规划指南

**三维规划模型**:  
| 维度 | 小型 | 中型 | 大型 |
|-----|------|------|------|
| 数据量 | < 100MB | 100MB - 1GB | 1GB - 100GB |
| 并发连接 | < 5 | 5 - 20 | 20 - 100 |
| QPS | < 100 | 100 - 1000 | 1000 - 10000 |
| 推荐配置 | 默认 | 优化缓存/WAL | 分区+读写分离 |

**增长预测公式**:  
```
所需容量 = 当前数据量 × (1 + 月增长率)^月份 × 安全系数(1.5)
```

### 精益数据库管理

**浪费识别与消除**:  
| 浪费类型 | 表现 | 消除措施 |
|---------|------|---------|
| 库存 | 未使用的索引 | 定期清理无用索引 |
| 等待 | 长时间锁等待 | 优化事务粒度 |
| 过度加工 | 不必要的约束 | 简化验证逻辑 |
| 缺陷 | Schema设计缺陷 | 设计评审+测试 |
| 动作 | 手动维护操作 | 自动化脚本 |

**5S数字工作区**:  
1. **整理**: 删除无用表、索引、触发器
2. **整顿**: 标准化命名规范、目录结构
3. **清扫**: 定期VACUUM、日志清理
4. **清洁**: 维护SOP标准化
5. **素养**: Code Review检查清单

### 约束管理

**系统约束识别**:  
1. **并发写入**: SQLite的锁机制限制
2. **大数据量**: 超内存数据查询性能下降
3. **备份窗口**: 大规模备份耗时

**挖尽约束策略**:  
```python
# 并发优化
PRAGMA journal_mode = WAL;        # 提升并发读
PRAGMA synchronous = NORMAL;      # 平衡安全与性能

# 大数据优化
PRAGMA cache_size = -65536;       # 64MB缓存
PRAGMA mmap_size = 268435456;     # 256MB内存映射

# 查询优化
CREATE INDEX ...                  # 针对性索引
ANALYZE;                          # 更新统计信息
```

**DBR调度**:  
- **Drum**: 以数据库写入能力为节拍
- **Buffer**: 应用层写入队列缓冲
- **Rope**: 连接池限制并发访问

### 六西格玛质量管理

**DMAIC改进流程**:  
1. **Define**: 定义数据库质量CTQ
2. **Measure**: 建立性能监控体系
3. **Analyze**: 分析慢查询和瓶颈
4. **Improve**: 实施索引优化、查询重写
5. **Control**: SPC控制图监控关键指标

**CTQ监控**:  
```python
from sqlite_manager import QualityMonitor

monitor = QualityMonitor(db)
monitor.track_query_latency()      # 查询延迟追踪
monitor.track_connection_pool()    # 连接池监控
monitor.track_table_sizes()        # 表大小监控
monitor.check_index_usage()        # 索引使用检查
monitor.generate_health_report()   # 健康报告
```

**查询优化检查清单**:  
- [ ] 是否使用了EXPLAIN QUERY PLAN分析?
- [ ] 是否避免了全表扫描?
- [ ] 是否使用了覆盖索引?
- [ ] 事务范围是否最小化?
- [ ] 是否使用了参数化查询?
- [ ] 大结果集是否使用了分页?

### 持续改进 (Kaizen)

**性能优化Kaizen**:  
- **目标**: 将慢查询比例从X%降低到<1%
- **方法**: 慢查询日志分析、自动优化建议
- **周期**: 每周审查

**容量规划Kaizen**:  
- **目标**: 提前30天预警容量不足
- **方法**: 趋势分析、增长预测
- **周期**: 每月评估

**改进审查清单**:  
- [ ] 每周慢查询日志分析
- [ ] 每月索引使用效率审查
- [ ] 每季度Schema设计评估
- [ ] 每半年灾难恢复演练

### 数据库健康检查脚本

```python
#!/usr/bin/env python3
"""SQLite健康检查脚本"""

from sqlite_manager import HealthCheck

def main():
    checker = HealthCheck('myapp.db')
    
    # 基础健康检查
    results = {
        'connectivity': checker.check_connectivity(),
        'integrity': checker.check_integrity(),
        'performance': checker.check_performance_baseline(),
        'storage': checker.check_storage_efficiency(),
        'indexes': checker.check_index_efficiency(),
        'backups': checker.check_backup_status()
    }
    
    # 生成报告
    report = checker.generate_report(results)
    
    # 告警判断
    if results['performance']['status'] != 'OK':
        print("⚠️ 性能告警: 查询延迟超标")
    
    if results['storage']['fragmentation'] > 0.3:
        print("⚠️ 存储告警: 建议执行VACUUM")
    
    return report

if __name__ == '__main__':
    main()
```

### 风险管理

**风险矩阵**:  
| 风险 | 概率 | 影响 | 缓解措施 |
|-----|------|------|---------|
| 数据库损坏 | 低 | 高 | 定期备份+完整性检查 |
| 性能下降 | 中 | 中 | 监控+自动优化 |
| 数据丢失 | 低 | 高 | WAL模式+备份策略 |
| 并发冲突 | 中 | 中 | 连接池+重试机制 |

---

## 参考来源

- **SQLite**: https://sqlite.org
- **SQLite Optimization**: https://sqlite.org/optoverview.html
- **Python sqlite3**: https://docs.python.org/3/library/sqlite3.html

---

## 版本信息

- **Version**: 2.0.0 (2025 增强版)
- **Author**: KbotGenesis
- **SQLite Version**: 3.45+
- **Last Updated**: 2026-02-19
- **Quality Report**: 参见 QUALITY_ANALYSIS_REPORT.md
