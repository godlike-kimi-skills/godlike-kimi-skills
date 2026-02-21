# 重磅发布！最全 Kimi Code CLI Skills 集合，18个生产级技能开源

> 从 0 到 18 个生产级 Skills，为中文开发者打造的 Kimi CLI 技能生态

---

## 项目背景

使用 Kimi Code CLI 一段时间后，我发现一个痛点：**每次新项目都要重复写相似的代码**。

- 数据库操作 → 重复写连接池
- API 测试 → 重复写请求封装  
- Docker 部署 → 重复写 Dockerfile

于是我在想：为什么不把这些**通用的开发能力**封装成 Skills，让 Kimi CLI 直接调用？

经过 2 周的开发，我开源了 **18 个生产级 Skills**，覆盖数据库、DevOps、开发工具等核心场景。

---

## 核心特性

- ✅ **开箱即用** - 安装即可使用，无需额外配置
- ✅ **中文文档** - 100% 中文 README 和使用示例
- ✅ **完整测试** - 每个 Skill 都包含单元测试
- ✅ **类型安全** - Python 类型注解全覆盖
- ✅ **MIT 协议** - 免费商用，欢迎 Fork

---

## 已包含 Skills 清单

### 🗄️ 数据库（3 个）
| Skill | 功能 |
|-------|------|
| postgres-skill | PostgreSQL 查询、迁移、备份 |
| mysql-skill | MySQL/MariaDB 管理 |
| redis-cache-skill | Redis 缓存操作 |

### 🚀 DevOps & 云（4 个）
| Skill | 功能 |
|-------|------|
| docker-skill | 容器管理、镜像构建 |
| kubernetes-skill | K8s 集群操作 |
| github-actions-skill | CI/CD 工作流生成 |
| nginx-skill | 配置管理、SSL 证书 |

### 💻 开发工具（5 个）
| Skill | 功能 |
|-------|------|
| http-client-skill | API 测试、请求调试 |
| git-analyzer-skill | 仓库分析、提交统计 |
| api-testing-skill | 自动化接口测试 |
| pytest-skill | 测试框架集成 |
| black-isort-skill | Python 代码格式化 |

### 🤖 AI/ML（3 个）
| Skill | 功能 |
|-------|------|
| huggingface-skill | 模型下载、推理 |
| openai-api-skill | OpenAI API 封装 |
| pandas-skill | 数据分析助手 |

### 🔒 安全（3 个）
| Skill | 功能 |
|-------|------|
| security-audit-skill | 代码安全审计 |
| dependency-check-skill | 依赖漏洞扫描 |
| secrets-scanner-skill | 敏感信息检测 |

---

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/godlike-kimi-skills/godlike-kimi-skills.git
cd godlike-kimi-skills

# 安装 Skill（以 PostgreSQL 为例）
kimi skill install ./skills/postgres-skill

# 使用 Skill
kimi skill run postgres-skill --params "action=query&sql=SELECT * FROM users"
```

### 更多使用示例

```bash
# Docker 操作
kimi skill run docker-skill --params "action=ps"
kimi skill run docker-skill --params "action=logs&container=myapp"

# API 测试
kimi skill run http-client-skill --params "method=GET&url=https://api.example.com"

# 代码格式化
kimi skill run black-isort-skill --params "path=./src"
```

---

## GitHub 链接

🔗 **https://github.com/godlike-kimi-skills/godlike-kimi-skills**

---

## 邀请 Star 和贡献

如果你觉得这个项目有用，欢迎：

- ⭐ **Star** - 给仓库点个 Star，让更多人看到
- 🍴 **Fork** - 基于此开发你自己的 Skills
- 📝 **PR** - 提交新的 Skill 或改进现有功能
- 💬 **Issue** - 反馈问题或建议

我们的目标是构建**最完整的中文 Kimi CLI 技能生态**。

---

**18 个 Skills 只是开始，目标是 100+！**

欢迎加入，一起让 AI 编程更高效 🚀
