# 🔥 Awesome Kimi Skills · 月神技能

> 🏮 **最全、最快、最强的 Kimi Code CLI Skills 集合**
> 
> **目标**: 成为 Kimi 生态的 Skills 标准参考  
> **中文优先** | **即插即用** | **社区驱动** | **AI运营**

<p align="center">
  <a href="https://awesome.re"><img src="https://awesome.re/badge.svg" alt="Awesome"></a>
  <a href="https://www.moonshot.cn/"><img src="https://img.shields.io/badge/Built%20for-Kimi-7C3AED?style=flat-square" alt="Kimi"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg?style=flat-square" alt="License"></a>
  <img src="https://img.shields.io/badge/🌙_Skills-224+-2C3E50?style=flat-square&labelColor=F5F5F0" alt="Skills" />
  <img src="https://img.shields.io/badge/🏮_Categories-7+-C9372C?style=flat-square&labelColor=F5F5F0" alt="Categories" />
  <img src="https://img.shields.io/badge/🐇_中文-100%25-D4AF37?style=flat-square&labelColor=F5F5F0" alt="Chinese" />
</p>

---

## 📖 中文说明

**月神技能 (Godlike Kimi Skills)** 是专为 [Kimi Code CLI](https://kimi.com/coding) 打造的中文Skills生态系统。

- 🌙 **文化主题**: 嫦娥月兔 × 中国美学
- 🤖 **AI运营**: 完全由AI Agent自主运营
- 🇨🇳 **中文优先**: 100%中文文档与示例
- 🏆 **质量认证**: 5级质量评级体系
- 🚀 **生产就绪**: 224+个生产级技能

---

## 🚀 快速开始

### 安装 Kimi CLI

```bash
# 安装 Kimi Code CLI
pip install kimi-cli

# 或使用 pipx (推荐)
pipx install kimi-cli
```

### 安装 Skills

```bash
# 方法1: 一键安装单个 Skill
kimi skill install https://github.com/godlike-kimi-skills/coding-agent

# 方法2: 手动克隆安装
git clone https://github.com/godlike-kimi-skills/godlike-kimi-skills.git
cp -r godlike-kimi-skills/skills/coding-agent ~/.kimi/skills/

# 方法3: 国内镜像加速 (Gitee)
git clone https://gitee.com/godlike-kimi-skills/awesome-kimi-skills.git
```

### 使用 Skills

```bash
# 列出已安装的 Skills
kimi skill list

# 运行 Skill
kimi skill run coding-agent

# 带参数运行
kimi skill run coding-agent --params "task=refactor&language=python"
```

---

## 📚 Skills 分类表格

### 🏮 桂树开发 / Development (40+ Skills)

| Skill | 描述 | 质量 | 安装命令 |
|-------|------|------|----------|
| [coding-agent](./skills/coding-agent/) | AI编码助手，智能代码生成与重构 | 🏆 AAA | `kimi skill install coding-agent` |
| [skill-creator-enhanced](./skills/skill-creator-enhanced/) | 一键生成Kimi Skill项目 | 🏆 AAA | `kimi skill install skill-creator-enhanced` |
| [mcp-builder](./skills/mcp-builder/) | MCP服务器构建器 | 🏆 AAA | `kimi skill install mcp-builder` |
| [git-toolkit](./skills/git-toolkit/) | Git自动化工具集 | 🥈 AA | `kimi skill install git-toolkit` |
| [dev-workflow](./skills/dev-workflow/) | 开发工作流优化 | 🥈 AA | `kimi skill install dev-workflow` |
| [debug-master](./skills/debug-master/) | 调试专家 | 🥈 AA | `kimi skill install debug-master` |

### 🤖 月影AI / AI Enhancement (15+ Skills)

| Skill | 描述 | 质量 | 安装命令 |
|-------|------|------|----------|
| [browser-use-skill](./skills/browser-use-skill/) | AI驱动的浏览器自动化 | 🏆 AAA | `kimi skill install browser-use-skill` |
| [huggingface-cli](./skills/huggingface-cli/) | HuggingFace模型管理 | 🥈 AA | `kimi skill install huggingface-cli` |
| [agent-browser](./skills/agent-browser/) | 智能代理浏览器 | 🥈 AA | `kimi skill install agent-browser` |
| [long-term-memory](./skills/long-term-memory/) | 跨会话长期记忆管理 | 🥈 AA | `kimi skill install long-term-memory` |
| [context-manager](./skills/context-manager/) | 上下文智能管理 | 🥈 AA | `kimi skill install context-manager` |

### 🐇 玉兔思维 / Thinking Frameworks (35+ Skills)

| Skill | 描述 | 质量 | 安装命令 |
|-------|------|------|----------|
| [first-principles](./skills/first-principles/) | 第一性原理思维 | 🏆 AAA | `kimi skill install first-principles` |
| [critical-thinking](./skills/critical-thinking/) | 批判性思维框架 | 🏆 AAA | `kimi skill install critical-thinking` |
| [system-thinking](./skills/system-thinking/) | 系统思维方法论 | 🏆 AAA | `kimi skill install system-thinking` |
| [mental-models-library](./skills/mental-models-library/) | 心智模型库 | 🥈 AA | `kimi skill install mental-models-library` |
| [bayesian-decision](./skills/bayesian-decision/) | 贝叶斯决策分析 | 🥈 AA | `kimi skill install bayesian-decision` |

### 📊 翠竹效率 / Productivity (25+ Skills)

| Skill | 描述 | 质量 | 安装命令 |
|-------|------|------|----------|
| [kanban-skill](./skills/kanban-skill/) | Markdown看板管理 | 🥈 AA | `kimi skill install kanban-skill` |
| [docx-skill](./skills/docx-skill/) | Word文档智能处理 | 🥈 AA | `kimi skill install docx-skill` |
| [workflow-builder](./skills/workflow-builder/) | 工作流自动化构建 | 🥈 AA | `kimi skill install workflow-builder` |
| [file-organizer](./skills/file-organizer/) | 智能文件整理 | 🥈 AA | `kimi skill install file-organizer` |
| [task-tracker](./skills/task-tracker/) | 任务追踪管理 | 🥈 AA | `kimi skill install task-tracker` |

### 🔒 金石安全 / Security (15+ Skills)

| Skill | 描述 | 质量 | 安装命令 |
|-------|------|------|----------|
| [owasp-security](./skills/owasp-security/) | OWASP安全标准指南 | 🏆 AAA | `kimi skill install owasp-security` |
| [security-check](./skills/security-check/) | 自动化安全检查 | 🥈 AA | `kimi skill install security-check` |
| [privacy-scanner](./skills/privacy-scanner/) | 隐私合规扫描 | 🥈 AA | `kimi skill install privacy-scanner` |
| [secrets-scanner-skill](./skills/secrets-scanner-skill/) | 密钥泄露扫描 | 🥈 AA | `kimi skill install secrets-scanner-skill` |

### 🌙 月华金融 / Finance (20+ Skills)

| Skill | 描述 | 质量 | 安装命令 |
|-------|------|------|----------|
| [akshare-connector](./skills/akshare-connector/) | A股数据实时连接 | 🥈 AA | `kimi skill install akshare-connector` |
| [china-macro-economic-tracker](./skills/china-macro-economic-tracker/) | 宏观经济追踪 | 🥈 AA | `kimi skill install china-macro-economic-tracker` |
| [stock-watcher](./skills/stock-watcher/) | A股/港股/美股实时监控 | 🥈 AA | `kimi skill install stock-watcher` |
| [crypto-wallet](./skills/crypto-wallet/) | 加密资产管理 | 🥈 AA | `kimi skill install crypto-wallet` |

### 🎋 玉简其他 / Others (74+ Skills)

| Skill | 描述 | 质量 | 安装命令 |
|-------|------|------|----------|
| [chinese-colors](./skills/chinese-colors/) | 中国传统色卡(100+色彩) | 🏆 AAA | `kimi skill install chinese-colors` |
| [chinese-lunar](./skills/chinese-lunar/) | 农历黄历与节气 | 🏆 AAA | `kimi skill install chinese-lunar` |
| [chinese-idioms](./skills/chinese-idioms/) | 成语典故与接龙 | 🏆 AAA | `kimi skill install chinese-idioms` |

---

## 📊 质量等级说明

| 等级 | 徽章 | 标准 | 数量 |
|------|------|------|------|
| 🏆 金印 | AAA | 生产级、完整测试、文档齐全 | 21+ |
| 🥈 银牌 | AA | 功能完整、良好文档 | 80+ |
| 🥉 铜牌 | A | 可用、基础文档 | 60+ |
| 📜 玉简 | B | 实验性、待完善 | 60+ |

---

## 📊 项目统计

```
总 Skills 数: 224+ (持续增加中...)
分类数: 7 大分类
质量等级: 5 级评级体系
最后更新: 2026-02-21
更新频率: 每日
```

---

## 🌟 特色功能

### 全中文支持
- 所有 Skills 都经过中文优化
- 针对中国开发者场景定制
- 支持中文文档和注释

### 即插即用
- 标准 Agent Skills 格式
- 一键安装，自动配置
- 兼容 Kimi Code CLI

### 每日更新
- 每日扫描竞品热门 Skills
- 第一时间移植到 Kimi
- 社区贡献快速审核

---

## 🤝 如何贡献

我们欢迎所有形式的贡献！

### 快速贡献指南

1. **Fork 本仓库**
2. **创建新 Skill** - 使用 [skill-creator-enhanced](./skills/skill-creator-enhanced/)
3. **提交 Pull Request** - 我们会快速审核

### 详细贡献指南

📖 查看完整 [贡献指南](./CONTRIBUTING.md) 了解：
- Skill 格式规范
- 质量评级标准
- 审核流程
- 命名规范

### 其他贡献方式

- ⭐ 给项目 Star
- 🐛 提交 Issue 报告Bug
- 💡 在 Discussions 分享想法
- 📢 帮助推广项目

---

## 🗺️ 路线图

| 阶段 | 目标 | 时间 |
|------|------|------|
| Day 1 | 20个核心 Skills 上线 | 2026-02-21 ✅ |
| Week 1 | 100个 Skills，完善文档 | 2026-02-28 |
| Month 1 | 300个 Skills，社区建设 | 2026-03-21 |
| Month 3 | 1000个 Skills，生态完善 | 2026-05-21 |

---

## 🌐 国内镜像

由于 GFW 影响，我们提供国内镜像加速访问：

| 镜像平台 | 地址 | 速度 | 推荐度 |
|---------|------|------|--------|
| **Gitee** | https://gitee.com/godlike-kimi-skills/awesome-kimi-skills | ⚡⚡⚡⚡⚡ | ⭐⭐⭐⭐⭐ |
| GitCode | https://gitcode.com/godlike-kimi-skills/awesome-kimi-skills | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ |

### 快速安装（国内版）

```bash
# 使用 Gitee 镜像克隆
git clone https://gitee.com/godlike-kimi-skills/awesome-kimi-skills.git
cd awesome-kimi-skills

# 安装 Skill
cp -r skills/coding-agent ~/.kimi/skills/
```

---

## 📞 联系我们

- 💬 [GitHub Discussions](../../discussions) - 社区讨论
- 🐛 [GitHub Issues](../../issues) - 技术讨论、Bug 报告
- 📧 邮件: (即将添加)

---

## 📄 许可证

[MIT License](./LICENSE) © Godlike Kimi Skills Team

---

<p align="center">
  <strong>Built with ❤️ for Kimi Community</strong><br>
  <sub>Made in China, For the World</sub>
</p>

<p align="center">
  <em>🏮 月之暗面，技传四方 🏮</em>
</p>
