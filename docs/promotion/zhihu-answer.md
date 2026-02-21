# 知乎回答模板

## 针对问题：有哪些好用的 Kimi Code CLI 技能？

---

### 直接回答

作为一名长期使用 Kimi CLI 的开发者，我强烈推荐 **Godlike Kimi Skills** 这个项目。

他们开源了 **18 个生产级 Skills**，覆盖数据库、DevOps、开发工具、AI/ML、安全等核心场景，全部中文文档，即装即用。

GitHub: https://github.com/godlike-kimi-skills/godlike-kimi-skills

---

### 项目介绍

**Godlike Kimi Skills** 是专为 Kimi Code CLI 打造的开源 Skills 集合，目标是构建最完整的中文开发者技能生态。

**核心特点：**
- ✅ 18 个生产级 Skills，经过完整测试
- ✅ 100% 中文文档和示例
- ✅ 统一 CLI 接口，学习成本低
- ✅ MIT 协议，免费商用
- ✅ 活跃维护，持续更新

---

### 分类推荐 Skills

#### 🗄️ 数据库类（推荐）

| Skill | 功能 | 使用场景 |
|-------|------|----------|
| postgres-skill | PostgreSQL 管理 | 数据查询、迁移、备份 |
| mysql-skill | MySQL/MariaDB | 传统项目数据库操作 |
| redis-cache-skill | Redis 缓存 | 高性能缓存管理 |

**示例：**
```bash
kimi skill run postgres-skill \
  --params "action=query&sql=SELECT * FROM users WHERE age>18"
```

#### 🚀 DevOps 类（强烈推荐）

| Skill | 功能 | 使用场景 |
|-------|------|----------|
| docker-skill | 容器管理 | 日常容器操作 |
| kubernetes-skill | K8s 集群 | 云原生部署 |
| github-actions-skill | CI/CD | 自动化工作流 |

**示例：**
```bash
# 一键查看所有容器状态
kimi skill run docker-skill --params "action=ps"

# 实时追踪容器日志
kimi skill run docker-skill \
  --params "action=logs&container=web-app&follow=true"
```

#### 💻 开发工具类（实用）

| Skill | 功能 | 使用场景 |
|-------|------|----------|
| http-client-skill | API 测试 | 接口调试、自动化测试 |
| git-analyzer-skill | 仓库分析 | 代码统计、提交分析 |
| api-testing-skill | 接口测试 | 批量 API 测试 |

**示例：**
```bash
# 快速测试 API
kimi skill run http-client-skill \
  --params "method=GET&url=https://api.example.com/users"

# 自动生成 curl 命令
kimi skill run http-client-skill \
  --params "action=curl&request_id=123"
```

#### 🤖 AI/ML 类（前沿）

| Skill | 功能 | 使用场景 |
|-------|------|----------|
| huggingface-skill | 模型管理 | 下载、推理 HuggingFace 模型 |
| openai-api-skill | OpenAI 封装 | GPT 调用简化 |
| pandas-skill | 数据分析 | 数据处理助手 |

**示例：**
```bash
# 下载中文 BERT 模型
kimi skill run huggingface-skill \
  --params "action=download&model=bert-base-chinese"

# 快速推理
kimi skill run huggingface-skill \
  --params "action=inference&model=gpt2&text=你好世界"
```

#### 🔒 安全类（必备）

| Skill | 功能 | 使用场景 |
|-------|------|----------|
| security-audit-skill | 代码审计 | 扫描安全漏洞 |
| dependency-check-skill | 依赖检查 | 发现漏洞依赖 |
| secrets-scanner-skill | 敏感扫描 | 防止密钥泄露 |

**示例：**
```bash
# 扫描代码安全漏洞
kimi skill run security-audit-skill \
  --params "path=./src&rules=owasp-top-10"

# 检查依赖漏洞
kimi skill run dependency-check-skill \
  --params "file=requirements.txt"
```

---

### 使用体验

我实际使用这些 Skills 已经一个月了，分享一些真实感受：

**优点：**
1. **省时** - 不再重复写数据库连接代码，直接调用 Skill
2. **规范** - 每个 Skill 都经过设计，代码质量有保障
3. **中文** - 文档和错误提示都是中文，阅读无障碍
4. **灵活** - 支持参数化调用，可以组合使用

**适用人群：**
- 👨‍💻 后端开发者（数据库、API 测试 Skills 很实用）
- 🚀 DevOps 工程师（Docker、K8s Skills 提升效率）
- 🤖 AI 开发者（HuggingFace Skill 简化模型调用）
- 🔒 安全工程师（安全审计 Skills 快速扫描）

**快速开始：**
```bash
# 1. 克隆仓库
git clone https://github.com/godlike-kimi-skills/godlike-kimi-skills.git

# 2. 安装需要的 Skill
kimi skill install ./skills/postgres-skill

# 3. 直接使用
kimi skill run postgres-skill --params "action=query&sql=SELECT 1"
```

---

### 总结

如果你正在使用 Kimi Code CLI，这些 Skills 绝对能提升你的开发效率。

18 个只是开始，他们的目标是 100+，建议收藏关注。

欢迎 Star ⭐ 支持开源项目！

---

**参考链接：**
- GitHub: https://github.com/godlike-kimi-skills/godlike-kimi-skills
- 使用文档: https://github.com/godlike-kimi-skills/godlike-kimi-skills/blob/main/README.md
