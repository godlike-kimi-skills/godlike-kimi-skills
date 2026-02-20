# Skills 文档最佳实践 - 全网权威总结

> 基于 Anthropic 官方文档 + 社区研究 (200+ Skills 测试)

---

## 📊 关键数据

| 描述优化程度 | 激活成功率 | 关键特征 |
|-------------|-----------|---------|
| 无优化 | ~20% | 默认行为 |
| 简单描述 | 20% | 模糊触发语言 |
| 优化描述 | 50% | 特定 USE WHEN 模式 |
| LLM预评估Hook | 80% | API预筛选 |
| 强制评估Hook | **84%** | 显式评估要求 |

**结论**：正确优化描述可将激活率从 20% 提升到 50%，添加示例可进一步提升到 72-90%

---

## 🎯 黄金法则：描述的两部分结构

每个 Skill 的 `description` 必须回答两个核心问题：

### 1. WHAT - 能力陈述
说明这个 Skill 能做什么

### 2. WHEN - 触发条件
说明什么时候应该调用这个 Skill

### ✅ 优秀示例

```yaml
# 好的描述（50%+ 激活率）
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.

# 更好的描述（包含具体关键词）
description: Analyze Excel spreadsheets, create pivot tables, generate charts. Use when analyzing Excel files, spreadsheets, tabular data, or .xlsx files.

# 使用 USE WHEN 模式
description: |
  Knowledge Management for Obsidian vault. USE WHEN user asks
  "what do I know about X", "find notes about", "load context
  for project", "save to vault", "capture this", "validate tags".
```

### ❌ 避免的描述

```yaml
# 太模糊（20% 激活率）
description: Helps with documents
description: Processes data
description: Does stuff with files

# 第一人称（避免）
description: I can help you process Excel files

# 第二人称（避免）
description: You can use this to process Excel files
```

---

## 📝 第三人称写作原则

描述会注入到系统提示中，必须保持第三人称：

| ✅ 正确的 | ❌ 避免的 |
|---------|---------|
| Processes Excel files and generates reports | I can help you process Excel files |
| Extracts text from PDF documents | You can use this to extract text |
| Creates PowerPoint presentations | I will create presentations for you |

---

## 🔑 USE WHEN 模式（最重要）

在描述中必须包含 "Use when..." 语言来明确定义触发条件：

### 模板格式

```yaml
description: |
  [核心功能]. 
  Use when [触发条件1], [触发条件2], or when user mentions "[关键词1]", "[关键词2]", "[关键词3]".
```

### 具体示例

| Skill | 触发条件示例 |
|-------|-------------|
| PDF处理 | Use when working with PDF files, extracting text, merging documents, or when user mentions "PDF", "extract", "merge" |
| Excel处理 | Use when analyzing Excel files, spreadsheets, tabular data, .xlsx files, or when user mentions "spreadsheet", "pivot", "chart" |
| React检查 | Use when reviewing React code, checking components, analyzing hooks, or when user mentions "React", "component", "hook" |
| 调试 | Use when debugging code, analyzing errors, tracing issues, or when user mentions "bug", "error", "debug", "fix" |

---

## 🚫 明确边界：设置 Out of Scope

定义 Skill **不做什么** 与定义它做什么同样重要：

```markdown
## Out of Scope

This skill does NOT:
- Handle scanned PDFs (use OCR skill instead)
- Create PDFs from scratch (use document-generation skill)
- Process password-protected files
- Perform image editing on PDFs
```

**好处**：
- 避免错误的 Skill 调用
- 提高准确率
- 帮助 AI 选择合适的 Skill

---

## 📋 具体性优于通用性

### ❌ 通用描述（20% 激活率）

```yaml
description: Helps with documents
description: Code review tool
description: Testing helper
```

### ✅ 具体描述（50%+ 激活率）

```yaml
# 文档处理
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.

# 代码审查
description: Review code for best practices, potential bugs, and maintainability. Use when reviewing pull requests, checking code quality, analyzing diffs, or when user mentions "review", "PR", "code quality", or "best practices".

# 测试
description: Generate test cases following TDD principles, create test templates, analyze test coverage. Use when writing tests, implementing TDD, checking coverage, or when user mentions "test", "TDD", "coverage", "unit test".
```

---

## 🔢 数字约束

| 字段 | 约束 |
|------|------|
| name | 最多64字符，小写字母/数字/连字符，无XML标签 |
| description | 最多1024字符，必须非空，无XML标签 |
| SKILL.md 正文 | 建议少于500行 |
| 完整可用技能列表 | 15,000字符限制 |

---

## 📂 推荐文件结构

```
skill-name/
├── SKILL.md              # 入口点（必需，<500行）
├── docs/                 # 参考文档
│   ├── CLI-REFERENCE.md
│   ├── CONCEPTS.md
│   └── EXAMPLES.md
├── workflows/            # 操作流程
│   ├── workflow-a.md
│   └── workflow-b.md
├── scripts/              # 可执行辅助脚本
│   └── helper.py
└── templates/            # 可重用模板
    └── template.txt
```

---

## 🧪 测试驱动的 Skill 开发

基于 40+ Skill 失败分析的五步法：

### 1. 识别差距
运行不带 Skill 的 Claude，记录失败

### 2. 创建评估
构建 3+ 测试场景

### 3. 建立基线
测量不带 Skill 的性能

### 4. 编写最小指令
只写足够通过评估的内容

### 5. 迭代
测试、比较、精炼

---

## 🎯 描述优化检查清单

### 结构
- [ ] SKILL.md 少于 500 行
- [ ] YAML frontmatter 包含 name 和 description
- [ ] 清晰的章节标题
- [ ] 复杂主题引用详细文档

### 描述
- [ ] 使用第三人称（无 "I" 或 "you"）
- [ ] 包含 "USE WHEN" 触发模式
- [ ] 具体关键词便于发现
- [ ] 少于 1024 字符
- [ ] 包含 5+ 个具体触发关键词
- [ ] 提及文件类型、格式或领域

### 示例
- [ ] 具体的，非抽象场景
- [ ] 展示预期的 Claude 行为
- [ ] 包含常见变体
- [ ] 示例长度超过规则部分
- [ ] 必要时演示多轮工作流

### 边界
- [ ] 明确的 Out of Scope 部分
- [ ] 定义 Skill 不做什么
- [ ] 替代方案建议

---

## 🏆 三层激活策略

### Level 1: 描述优化（低投入，50% 成功率）
- 使用特定的 "Use when" 语言
- 包含工作流中的确切关键词
- 添加文件类型提及

### Level 2: CLAUDE.md 引用（中等投入，60-70% 成功率）
- 在项目 CLAUDE.md 中记录 Skill 使用模式
- 为常见任务引用特定 Skills
- 创建工作流文档

### Level 3: 自定义 Hooks（高投入，84% 成功率）
- 实现强制评估 hooks
- 要求显式 Skill 推理
- 创建承诺机制

**建议**：所有 Skill 从 Level 1 开始，关键工作流升级到 Level 3

---

## 📖 实际案例

### 案例 1: Excel 处理 Skill

**优化前（20% 激活率）**:
```yaml
description: Helps with Excel files
```

**优化后（50%+ 激活率）**:
```yaml
description: Analyze Excel spreadsheets, create pivot tables, generate charts, process CSV data. Use when analyzing Excel files, spreadsheets, tabular data, .xlsx files, or when user mentions "spreadsheet", "pivot", "chart", "formula", "cell", "worksheet".
```

### 案例 2: TDD Skill

**优化前**:
```yaml
description: Test-driven development helper
```

**优化后**:
```yaml
description: Generate test cases following TDD principles, create test templates, analyze test coverage, guide red-green-refactor workflow. Use when writing tests, implementing TDD, checking coverage, or when user mentions "test", "TDD", "coverage", "unit test", "red-green-refactor", "test-first".
```

---

## 📚 参考资源

### 官方文档
- [Skill Authoring Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Agent Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Anthropic Skills GitHub](https://github.com/anthropics/skills)

### 社区研究
- [Writing Claude Skills That Actually Work](https://medium.com/@creativeaininja/writing-claude-skills-that-actually-work)
- [Claude Agent Skills Deep Dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)
- [How to Make Skills Activate Reliably](https://scottspence.com/posts/how-to-make-claude-code-skills-activate-reliably)
- [40+ Skill Failures Analysis](https://cashandcache.substack.com/p/i-analyzed-40-claude-skills-failures)

---

*文档整理时间: 2026-02-20*
*数据来源: Anthropic官方文档 + 社区200+ Skills测试*
