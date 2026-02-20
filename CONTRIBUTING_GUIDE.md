# 高质量Skill开发与提交完整指南

> 🤖 **本项目完全由 Wang Johnny 的 Kimi Code CLI 人工智能 Agents 生成和运营**

---

## 📋 目录 / Table of Contents

1. [核心准入标准 / Core Standards](#核心准入标准)
2. [开发规范 / Development Standards](#开发规范)
3. [提交规范 / Commit Convention](#提交规范)
4. [质量检查清单 / Quality Checklist](#质量检查清单)
5. [发布流程 / Release Process](#发布流程)

---

## 核心准入标准

### 高质量Skill的7大标准

| 标准 | 中文要求 | English Requirement |
|------|---------|---------------------|
| **标准合规** | 100%遵循Anthropic Agent Skill开放标准 | 100% comply with Anthropic Agent Skill standards |
| **专精可用** | 聚焦单一核心场景，解决明确痛点 | Focus on single core scenario, solve clear pain point |
| **安全无风险** | 无恶意代码、无硬编码敏感信息 | No malicious code, no hardcoded secrets |
| **零幻觉可追溯** | 所有输出有明确依据、可验证 | All outputs verifiable, traceable |
| **开箱即用** | 极简安装、完整示例、小白友好 | Minimal setup, complete examples, beginner-friendly |
| **兼容稳定** | 跨平台兼容(Win/Mac/Linux)、错误处理完善 | Cross-platform, robust error handling |
| **可维护可迭代** | 规范版本管理、完整文档、开源协议 | Version management, documentation, open source license |

---

## 开发规范

### 目录结构 / Directory Structure

```
your-skill-name/
├── SKILL.md                 # 【必填】技能描述文件（替代skill.json）
├── README.md                # 【必填】用户文档
├── LICENSE                  # 【必填】开源协议，推荐MIT
├── scripts/                 # 【必填】脚本目录
│   ├── main.py             # 核心入口脚本
│   └── utils.py            # 工具函数（可选）
├── requirements.txt         # 【必填】依赖声明
├── tests/                   # 【推荐】测试用例
│   └── test_basic.py
├── examples/                # 【推荐】使用示例
│   └── example1.py
├── .gitignore              # 【必填】Git忽略规则
└── docs/                   # 【可选】详细文档
    └── advanced-usage.md
```

### SKILL.md 规范 / SKILL.md Specification

必须包含以下字段（中英文双语）：

```markdown
---
name: your-skill-name
description: |
  中文描述：这个skill是做什么的，解决什么痛点
  English description: What this skill does, what pain point it solves
metadata:
  author: your-github-username
  version: 1.0.0
  category: 所属类别
  tags: [tag1, tag2, tag3]
  license: MIT
  min_cli_version: "0.5.0"
  platforms: [windows, macos, linux]
---

# Skill中文名称 / Skill English Name

## 简介 / Introduction

中文描述...
English description...

## 功能特性 / Features

- 特性1 / Feature 1
- 特性2 / Feature 2

## 安装 / Installation

```bash
kimi install your-skill-name
```

## 使用示例 / Usage Examples

### 示例1 / Example 1

中文说明...
English description...

```
示例代码
```

## 参数说明 / Parameters

| 参数名 | 类型 | 必填 | 默认值 | 中文说明 | English Description |
|--------|------|------|--------|----------|---------------------|
| param1 | string | 是 | 无 | 说明 | Description |

## 依赖要求 / Requirements

- Python 3.10+
- 其他依赖 / Other dependencies

## 更新日志 / Changelog

### v1.0.0 (YYYY-MM-DD)
- 初始发布 / Initial release
```

### 代码开发黄金法则 / Code Development Rules

1. **极简依赖原则 / Minimal Dependencies**
   - 能用内置库就不用第三方
   - 必须用的依赖锁定版本

2. **零硬编码原则 / No Hardcoded Secrets**
   - 禁止硬编码API Key、Token
   - 敏感信息通过环境变量传入

3. **完善错误处理 / Robust Error Handling**
   - 所有可能出错环节try-except
   - 给用户清晰错误提示

4. **标准化输入输出 / Standardized I/O**
   - 输出结构化格式（JSON/Markdown）
   - 适配AI终端解析

5. **无副作用原则 / No Side Effects**
   - 默认不修改本地文件
   - 高危操作需用户确认

6. **幻觉防控 / Hallucination Prevention**
   - 所有输出有逻辑依据
   - 引用内容标注来源

### 安全红线 / Security Red Lines

❌ **绝对禁止 / Absolutely Forbidden:**

- 硬编码API Key、密钥、Token
- 隐藏远程代码执行、数据上传
- 加密、混淆代码片段
- 批量创建垃圾文件、修改系统配置
- 加密货币/区块链无授权操作
- 重复、抄袭、同质化技能

---

## 提交规范

### 🚨 强制规则 / Mandatory Rule

**所有提交必须使用中英文双语，中文在前**

**All commits must be bilingual, Chinese first**

### 提交格式 / Commit Format

```
<类型>: <中文描述> / <English description>

<详细中文说明>
<Detailed English description>

- 变更点1 / Change 1
- 变更点2 / Change 2
```

### 提交类型 / Commit Types

| 类型 | 中文 | English | 使用场景 |
|------|------|---------|----------|
| `feat` | 功能 | Feature | 新增Skill或功能 |
| `fix` | 修复 | Bug Fix | 修复Bug |
| `docs` | 文档 | Documentation | 仅文档更新 |
| `style` | 格式 | Code Style | 代码格式（不影响功能）|
| `refactor` | 重构 | Refactoring | 代码重构 |
| `perf` | 性能 | Performance | 性能优化 |
| `test` | 测试 | Tests | 测试相关 |
| `chore` | 构建 | Chores | 构建/工具/依赖更新 |
| `ci` | 持续集成 | CI | CI/CD配置 |
| `security` | 安全 | Security | 安全修复 |
| `revert` | 回滚 | Revert | 回滚提交 |

### 提交示例 / Commit Examples

#### 新增Skill / Adding Skill

```
feat: 添加贝叶斯决策审计skill / Add bayesian decision audit skill

添加基于贝叶斯认知判定框架的决策审计功能
Add decision audit based on Bayesian cognitive framework

- 支持先验合理性校验 / Support prior rationality check
- 支持证据似然比计算 / Support evidence likelihood calculation
- 支持认知偏差审计 / Support cognitive bias audit
- 包含完整测试用例 / Include complete test cases

Closes #123
```

#### 修复Bug / Bug Fix

```
fix: 修复Windows路径兼容性问题 / Fix Windows path compatibility

修复在Windows环境下文件路径分隔符导致的错误
Fix file path separator error on Windows

- 统一使用os.path.join处理路径 / Use os.path.join for paths
- 添加Windows环境测试 / Add Windows environment test

Fixes #456
```

#### 更新文档 / Documentation

```
docs: 更新README安装说明和示例 / Update README installation guide

添加Windows详细安装步骤和常见问题解答
Add detailed Windows installation steps and FAQ

- 添加截图说明 / Add screenshot instructions
- 添加视频教程链接 / Add video tutorial links
- 更新参数说明表格 / Update parameter table
```

#### 安全修复 / Security Fix

```
security: 修复敏感信息泄露风险 / Fix sensitive info leak risk

移除代码中硬编码的测试API Key，改为环境变量读取
Remove hardcoded test API Key, use environment variable instead

- 添加.env.example文件 / Add .env.example file
- 更新文档说明环境变量配置 / Update docs for env var config

Security: CVE-2026-xxxx
```

### 提交检查清单 / Commit Checklist

提交前必须确认 / Must confirm before commit:

- [ ] 提交信息符合双语规范 / Commit message follows bilingual convention
- [ ] 中文在前，英文在后 / Chinese first, English second
- [ ] 类型标签正确 / Type label correct
- [ ] 标题不超过72字符 / Title within 72 characters
- [ ] 代码已本地测试 / Code tested locally
- [ ] 无硬编码敏感信息 / No hardcoded secrets

---

## 质量检查清单

### 开发完成后5项必做测试

#### 1. 核心功能测试 / Core Function Test

- [ ] 覆盖所有必填/非必填参数场景
- [ ] 正常场景：输入符合要求，验证输出
- [ ] 异常场景：输入错误，验证友好提示
- [ ] 边界场景：极端输入、超大内容

#### 2. 跨平台兼容测试 / Cross-platform Test

- [ ] Windows环境测试（必须）
- [ ] MacOS/Linux环境测试
- [ ] 路径分隔符兼容处理
- [ ] 依赖安装正常

#### 3. 安全审计自查 / Security Audit

- [ ] 无硬编码API Key/Token
- [ ] 无高危系统命令
- [ ] 依赖为官方稳定版
- [ ] 无隐藏网络请求

#### 4. 小白用户可用性测试 / Beginner Test

- [ ] README命令一键安装成功
- [ ] 示例命令复制即可执行
- [ ] 无未说明的前置依赖

#### 5. 性能与稳定性测试 / Performance Test

- [ ] 启动速度正常，无卡顿
- [ ] 无内存泄漏
- [ ] 大输入场景稳定

---

## 发布流程

### 阶段1: 本地准备 / Local Preparation

1. **完成功能开发 / Complete Development**
   - 所有功能实现完毕
   - 代码通过本地测试

2. **完善文档 / Complete Documentation**
   - SKILL.md 完整
   - README.md 完整
   - 示例代码可运行

3. **版本号确认 / Version Confirmation**
   - 遵循语义化版本号
   - SKILL.json version已更新

### 阶段2: 提交审核 / Submit for Review

1. **创建分支 / Create Branch**
   ```bash
   git checkout -b feat/your-skill-name
   ```

2. **提交更改 / Commit Changes**
   ```bash
   git add .
   git commit -m "feat: 添加XXX skill / Add XXX skill
   
   详细中文描述
   Detailed English description
   
   - 功能点1 / Feature 1
   - 功能点2 / Feature 2"
   ```

3. **推送到远程 / Push to Remote**
   ```bash
   git push origin feat/your-skill-name
   ```

4. **创建Pull Request**
   - 使用PR模板
   - 填写双语描述
   - 关联相关Issue

### 阶段3: 审核与合并 / Review & Merge

1. **自动化检查 / Automated Checks**
   - CI构建通过
   - 代码风格检查通过
   - 安全扫描通过

2. **人工审核 / Manual Review**
   - 代码质量审核
   - 文档完整性审核
   - 安全合规审核

3. **合并发布 / Merge & Release**
   - 合并到main分支
   - 打版本标签
   - 发布Release

### 语义化版本号规范 / Semantic Versioning

| 版本变化 | 场景 | 示例 |
|----------|------|------|
| **主版本** (X.0.0) | 破坏性变更 | API接口改变、不兼容旧版本 |
| **次版本** (0.X.0) | 新增功能 | 新增技能、新增参数 |
| **补丁版本** (0.0.X) | Bug修复 | 修复错误、优化性能 |

---

## 新手避坑TOP10

1. ❌ 大而全的臃肿技能 → ✅ 小而美的单一场景
2. ❌ 硬编码敏感信息 → ✅ 环境变量传入
3. ❌ 依赖地狱 → ✅ 极简依赖原则
4. ❌ 无文档无示例 → ✅ 完整README
5. ❌ 不遵守规范 → ✅ 严格遵循标准
6. ❌ 无错误处理 → ✅ 完善try-except
7. ❌ 重复造轮子 → ✅ 先做竞品排查
8. ❌ 系统专属代码 → ✅ 跨平台兼容
9. ❌ 无测试用例 → ✅ 核心功能测试
10. ❌ 发布后就不管 → ✅ 长期维护迭代

---

## 快速开始模板

### 最小可用Skill模板

```bash
# 1. 复制模板目录
cp -r templates/skill-template my-new-skill
cd my-new-skill

# 2. 编辑SKILL.md，填写你的技能信息
# 3. 编辑scripts/main.py，实现核心逻辑
# 4. 本地测试
python scripts/main.py

# 5. 提交
 git add .
git commit -m "feat: 添加XXX skill / Add XXX skill"
git push origin main
```

---

**让我们共同打造高质量的中文AI Skill生态！** 🚀  
**Let's build a high-quality Chinese AI Skill ecosystem together!** 🚀
