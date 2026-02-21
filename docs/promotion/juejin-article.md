# 我花了 24 小时，为 Kimi CLI 打造了一套完整的技能生态

> 从想法到 18 个生产级 Skills，记录我的开源实践

---

## 引言：我遇到的问题

作为一名全栈开发者，我每天都会用到 Kimi Code CLI。它确实提高了我的编码效率，但有一个问题一直困扰着我：

**重复造轮子**。

每次开始新项目，我都要：
- 重新写 PostgreSQL 的连接和查询代码
- 重新封装 Docker API 调用
- 重新写 API 测试的工具函数

这些代码 90% 都是重复的，为什么不能复用？

直到有一天，我发现 Kimi CLI 支持 **Skills 机制** —— 可以将常用的开发能力封装成可复用的模块。

于是，我决定：为中文开发者打造一套完整的 Skills 生态。

---

## 项目介绍：Godlike Kimi Skills

**Godlike Kimi Skills** 是一个面向 Kimi Code CLI 的开源 Skills 集合，专注于解决中文开发者的实际问题。

### 核心特点

| 特点 | 说明 |
|------|------|
| 中文优先 | 100% 中文文档和示例 |
| 生产可用 | 每个 Skill 都有完整测试 |
| 即装即用 | 安装后即可通过 Kimi CLI 调用 |
| 持续更新 | 计划扩展到 100+ Skills |

---

## 技术架构：如何组织

### Skill 标准结构

每个 Skill 都遵循统一的 7 文件结构：

```
skill-name/
├── skill.json          # 元数据和配置
├── SKILL.md            # 使用文档
├── main.py             # 核心实现
├── test_skill.py       # 单元测试
├── requirements.txt    # 依赖
├── README.md           # 说明文档
└── LICENSE             # MIT 许可证
```

### 关键技术决策

1. **Python 为主** - 开发效率高，生态丰富
2. **类型注解全覆盖** - 保证代码质量
3. **CLI 接口统一** - 所有 Skill 使用相同的调用方式
4. **Use When 关键词** - 提升 Skill 的触发准确率

---

## 精选 Skills 介绍

让我详细介绍几个代表性的 Skills：

### 1. postgres-skill - 数据库管理利器

```python
# 一键查询
kimi skill run postgres-skill --params "action=query&sql=SELECT * FROM users"

# 自动迁移
kimi skill run postgres-skill --params "action=migrate&file=schema.sql"

# 数据导出
kimi skill run postgres-skill --params "action=export&table=orders&format=csv"
```

**亮点**：内置连接池管理，自动处理并发请求。

### 2. docker-skill - 容器操作助手

```python
# 查看容器状态
kimi skill run docker-skill --params "action=ps"

# 查看实时日志
kimi skill run docker-skill --params "action=logs&container=web-app&follow=true"

# 构建镜像
kimi skill run docker-skill --params "action=build&tag=myapp:v1&path=."
```

**亮点**：支持批量操作，自动解析容器名称。

### 3. http-client-skill - API 测试专家

```python
# GET 请求
kimi skill run http-client-skill --params "method=GET&url=https://api.example.com/users"

# POST 带认证
kimi skill run http-client-skill --params "method=POST&url=https://api.example.com/data&headers={'Authorization':'Bearer token'}"

# 批量测试
kimi skill run http-client-skill --params "action=batch&file=tests.json"
```

**亮点**：自动生成 curl 命令，方便调试。

### 4. security-audit-skill - 代码安全审计

```python
# 扫描代码漏洞
kimi skill run security-audit-skill --params "path=./src&rules=owasp-top-10"

# 检查依赖
kimi skill run security-audit-skill --params "action=deps&file=requirements.txt"

# 生成报告
kimi skill run security-audit-skill --params "action=report&format=html"
```

**亮点**：集成多种安全规则，支持自定义检测。

### 5. huggingface-skill - AI 模型管理

```python
# 下载模型
kimi skill run huggingface-skill --params "action=download&model=bert-base-chinese"

# 模型推理
kimi skill run huggingface-skill --params "action=inference&model=gpt2&text=你好"

# 查看模型信息
kimi skill run huggingface-skill --params "action=info&model=meta-llama/Llama-2-7b"
```

**亮点**：自动处理 HuggingFace 的认证和缓存。

---

## 如何使用

### 安装单个 Skill

```bash
# 克隆仓库
git clone https://github.com/godlike-kimi-skills/godlike-kimi-skills.git

# 安装指定 Skill
kimi skill install ./skills/postgres-skill
```

### 批量安装

```bash
# 安装所有数据库相关 Skills
for skill in postgres-skill mysql-skill redis-cache-skill; do
    kimi skill install ./skills/$skill
done
```

### 在项目中使用

```python
# 在代码中调用
result = kimi.skill.run("postgres-skill", {
    "action": "query",
    "sql": "SELECT COUNT(*) FROM users"
})
```

---

## 未来规划

### 短期目标（1-2 个月）
- [ ] Skills 数量扩展到 30+
- [ ] 增加更多数据库支持（MongoDB、Elasticsearch）
- [ ] 完善测试覆盖率到 90%+

### 中期目标（3-6 个月）
- [ ] 建立 Skill 市场，支持一键安装
- [ ] 增加云端 Skills，无需本地安装
- [ ] 支持更多编程语言（JavaScript、Go）

### 长期愿景
- [ ] 100+ 生产级 Skills
- [ ] 成为 Kimi CLI 官方推荐生态
- [ ] 建立中文开发者社区

---

## 参与贡献

我们欢迎各种形式的贡献：

### 1. 提交新 Skill

参考 [Skill 创建指南](https://github.com/godlike-kimi-skills/godlike-kimi-skills/blob/main/CONTRIBUTING.md)，按照标准结构提交 PR。

### 2. 完善文档

帮助翻译文档、补充使用示例、修复 typo。

### 3. 反馈问题

通过 Issue 反馈 bug 或提出功能建议。

### 4. 分享推广

在社交媒体上分享这个项目，让更多人知道。

---

## 结语

24 小时的开发，18 个 Skills，这只是开始。

我相信，**好的开发工具应该让开发者专注于业务逻辑，而不是重复造轮子**。

Godlike Kimi Skills 就是要解决这个问题。

如果你也认同这个理念，欢迎加入我们：

- ⭐ **GitHub**: https://github.com/godlike-kimi-skills/godlike-kimi-skills
- 💬 **讨论**: 欢迎在 Issue 区交流

让我们一起，让 AI 编程更高效！

---

> 🌙 月之暗面，技传四方
