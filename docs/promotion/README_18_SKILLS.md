# 🚀 Godlike Kimi Skills - 18 个生产级 Skill 集合

[![Skills Count](https://img.shields.io/badge/Skills-18-blue)](./skills)
[![License](https://img.shields.io/badge/License-MIT-yellow)]()
[![Language](https://img.shields.io/badge/Language-中文-red)]()

> **专为 Kimi Code CLI 打造的 18 个生产级开源 Skills，涵盖数据库、DevOps、AI/ML、安全等核心领域**

---

## 📦 快速开始

```bash
# 克隆仓库
git clone https://github.com/godlike-kimi-skills/godlike-kimi-skills.git

# 安装 Skill（以 PostgreSQL 为例）
kimi skill install ./skills/postgres-skill

# 使用 Skill
kimi skill run postgres-skill --params "action=query&sql=SELECT * FROM users"
```

---

## 📚 Skills 分类

### 🗄️ 数据库（3 个）
| Skill | 描述 | 使用场景 |
|-------|------|----------|
| postgres-skill | PostgreSQL 查询和管理 | 数据查询、迁移、备份 |
| mysql-skill | MySQL/MariaDB 管理 | 传统关系型数据库操作 |
| redis-cache-skill | Redis 缓存管理 | 高性能缓存读写 |

### 🚀 DevOps & 云（4 个）
| Skill | 描述 | 使用场景 |
|-------|------|----------|
| docker-skill | Docker 容器管理 | 容器操作、镜像构建 |
| kubernetes-skill | K8s 集群管理 | 云原生应用部署 |
| github-actions-skill | GitHub Actions 工作流 | CI/CD 自动化 |
| nginx-skill | Nginx 配置管理 | 反向代理、SSL 证书 |

### 💻 开发工具（5 个）
| Skill | 描述 | 使用场景 |
|-------|------|----------|
| http-client-skill | HTTP 客户端和 API 测试 | 接口调试、请求发送 |
| git-analyzer-skill | Git 仓库分析 | 代码统计、提交分析 |
| api-testing-skill | API 自动化测试 | 批量接口测试 |
| pytest-skill | PyTest 测试框架 | Python 单元测试 |
| black-isort-skill | Python 代码格式化 | 代码风格统一 |

### 🤖 AI/ML（3 个）
| Skill | 描述 | 使用场景 |
|-------|------|----------|
| huggingface-skill | Hugging Face 模型管理 | 模型下载、推理 |
| openai-api-skill | OpenAI API 调用 | GPT 模型调用简化 |
| pandas-skill | Pandas 数据分析 | 数据处理、分析 |

### 🔒 安全（3 个）
| Skill | 描述 | 使用场景 |
|-------|------|----------|
| security-audit-skill | 代码安全审计 | 漏洞扫描、安全检测 |
| dependency-check-skill | 依赖漏洞检查 | 第三方库安全检查 |
| secrets-scanner-skill | 敏感信息扫描 | 密钥、密码泄露检测 |

---

## 🌟 特色功能

### ✅ 所有 Skill 都包含
- **完整 7 文件结构** - skill.json, SKILL.md, main.py, tests/, README, LICENSE, requirements
- **Use When 触发关键词** - 提升 Skill 触发准确率
- **详细中文文档** - API 参考和使用示例
- **完整测试覆盖** - 单元测试保障质量
- **MIT 许可证** - 开源免费商用
- **类型注解** - Python 类型安全
- **统一 CLI 接口** - 一致的调用方式

---

## 📖 使用示例

### PostgreSQL Skill
```bash
# 查询数据
kimi skill run postgres-skill --params "action=query&sql=SELECT * FROM users"

# 查看表结构
kimi skill run postgres-skill --params "action=schema&table=users"

# 导出数据
kimi skill run postgres-skill --params "action=export&table=users&format=csv"
```

### Docker Skill
```bash
# 列出容器
kimi skill run docker-skill --params "action=ps"

# 查看日志
kimi skill run docker-skill --params "action=logs&container=my-container"

# 构建镜像
kimi skill run docker-skill --params "action=build&tag=myapp:v1&path=."
```

### HTTP Client Skill
```bash
# GET 请求
kimi skill run http-client-skill --params "method=GET&url=https://api.example.com"

# POST 请求
kimi skill run http-client-skill --params "method=POST&url=https://api.example.com/data&body={'key':'value'}"

# 批量测试
kimi skill run http-client-skill --params "action=batch&file=tests.json"
```

### Security Audit Skill
```bash
# 扫描代码漏洞
kimi skill run security-audit-skill --params "path=./src&rules=owasp-top-10"

# 检查依赖
kimi skill run security-audit-skill --params "action=deps&file=requirements.txt"

# 生成报告
kimi skill run security-audit-skill --params "action=report&format=html"
```

---

## 🏗️ 项目结构

```
godlike-kimi-skills/
├── skills/                    # 所有 Skills 目录
│   ├── postgres-skill/
│   │   ├── skill.json        # Skill 元数据
│   │   ├── SKILL.md          # 技能文档
│   │   ├── main.py           # 主实现
│   │   ├── test_skill.py     # 测试文件
│   │   ├── requirements.txt  # 依赖
│   │   ├── README.md         # 说明文档
│   │   └── LICENSE           # MIT 许可证
│   ├── docker-skill/
│   ├── kubernetes-skill/
│   └── ... (15 more)
├── docs/                      # 文档
│   └── promotion/            # 推广资料
├── README.md                  # 本文件
└── CONTRIBUTING.md            # 贡献指南
```

---

## 🤝 贡献指南

1. Fork 本仓库
2. 创建新的 Skill 目录
3. 按照标准结构添加文件
4. 提交 Pull Request

### Skill 标准结构
```
my-skill/
├── skill.json          # 必须
├── SKILL.md            # 必须
├── main.py             # 必须
├── test_skill.py       # 必须
├── requirements.txt    # 必须
├── README.md           # 必须
└── LICENSE             # MIT
```

---

## 🎯 路线图

### 短期（1-2 个月）
- [ ] Skills 数量扩展到 30+
- [ ] 增加 MongoDB、Elasticsearch 支持
- [ ] 完善测试覆盖率到 90%+

### 中期（3-6 个月）
- [ ] 建立 Skill 市场
- [ ] 增加云端 Skills
- [ ] 支持更多编程语言

### 长期（6-12 个月）
- [ ] 100+ 生产级 Skills
- [ ] 成为 Kimi CLI 官方推荐生态
- [ ] 建立中文开发者社区

---

## 📄 许可证

所有 Skills 均采用 [MIT License](./LICENSE) 开源许可证。

---

## 🙏 致谢

- [Kimi](https://www.moonshot.cn) - Kimi Code CLI
- 所有开源贡献者

---

<p align="center">
  <em>🏮 月之暗面，技传四方 🏮</em>
</p>

<p align="center">
  <strong>18 Skills, One Mission: Make AI Coding Better</strong>
</p>
