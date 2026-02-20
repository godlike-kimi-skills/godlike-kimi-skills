# Skill 优化指南 - 添加 Use When 和 Out of Scope

## 快速优化步骤

### 第1步：更新 skill.json 的 description

每个 Skill 的 description 必须遵循：
```
[核心功能]. Use when [触发条件1], [触发条件2], or when user mentions "[关键词1]", "[关键词2]".
```

### 第2步：在 SKILL.md 中添加 "何时使用" 章节

### 第3步：在 SKILL.md 中添加 "Out of Scope" 章节

---

## 18个 Skills 的优化对照表

| Skill | 优化前 Description | 优化后 Description |
|-------|-------------------|-------------------|
| skill-creator-enhanced | 一键创建符合开源标准的Kimi Skill项目 | 一键创建符合开源标准的Kimi Skill项目，自动生成标准化文件和测试模板。Use when creating new skills, scaffolding projects, or when user mentions "create skill", "skill template", "scaffold" |
| docx-skill | 创建、编辑、格式化Word文档 | 创建、编辑、格式化Word文档(.docx)，支持模板、表格、图片插入。Use when working with Word documents, creating reports, or when user mentions "docx", "Word", "document", "report" |
| pdf-skill | 提取、创建、合并PDF文件 | 提取、创建、合并、转换PDF文件，支持文本提取和页面操作。Use when processing PDF files, extracting text, merging documents, or when user mentions "PDF", "extract", "merge" |
| xlsx-skill | 读取、写入、格式化Excel文件 | 读取、写入、格式化Excel文件，支持公式、图表、数据分析。Use when analyzing Excel files, spreadsheets, tabular data, or when user mentions "Excel", "spreadsheet", "xlsx", "chart" |
| pptx-skill | 创建、编辑PowerPoint演示文稿 | 创建、编辑PowerPoint演示文稿，支持模板、图表、幻灯片管理。Use when creating presentations, slides, or when user mentions "PowerPoint", "pptx", "presentation", "slide" |
| mcp-builder | 快速构建MCP服务器 | 快速构建MCP(Model Context Protocol)服务器，集成外部API和工具。Use when building MCP servers, creating API integrations, or when user mentions "MCP", "server", "API integration" |
| systematic-debugging | 结构化的bug定位和修复方法论 | 结构化的bug定位和修复方法论，支持多种编程语言。Use when debugging code, analyzing errors, tracing issues, or when user mentions "debug", "bug", "error", "trace", "fix" |
| test-driven-development | TDD工作流指导 | TDD工作流指导，生成测试用例和覆盖率分析。Use when writing tests, implementing TDD, checking coverage, or when user mentions "test", "TDD", "coverage", "unit test" |
| browser-use-skill | AI浏览器自动化 | AI浏览器自动化，支持网页浏览、表单填写、数据提取。Use when automating browser tasks, web scraping, form filling, or when user mentions "browser", "web", "scrape", "automation" |
| react-best-practices | React开发最佳实践 | React开发最佳实践，代码审查和性能优化检查。Use when reviewing React code, checking components, or when user mentions "React", "component", "hook", "JSX" |
| next-best-practices | Next.js开发最佳实践 | Next.js开发最佳实践，App Router和性能优化检查。Use when reviewing Next.js code, checking App Router, or when user mentions "Next.js", "App Router", "SSR", "SSG" |
| owasp-security | OWASP安全标准检查 | OWASP安全标准检查，漏洞检测和合规审查。Use when reviewing code security, checking vulnerabilities, or when user mentions "security", "OWASP", "vulnerability", "audit" |
| huggingface-cli | HuggingFace Hub CLI工具 | HuggingFace Hub CLI工具，模型和数据集管理。Use when downloading ML models, accessing HuggingFace, or when user mentions "HuggingFace", "model", "dataset", "transformer" |
| wrangler-skill | Cloudflare Wrangler CLI封装 | Cloudflare Wrangler CLI封装，Workers部署和管理。Use when deploying to Cloudflare, managing Workers, or when user mentions "Cloudflare", "Wrangler", "Workers", "edge" |
| shadcn-ui | shadcn/ui组件库集成 | shadcn/ui组件库集成，组件安装和管理。Use when installing UI components, managing shadcn/ui, or when user mentions "shadcn", "component", "UI", "Tailwind" |
| kanban-skill | Markdown-based Kanban board | Markdown-based Kanban board，纯文件看板管理。Use when managing tasks, creating kanban boards, or when user mentions "kanban", "task", "board", "todo" |
| youtube-transcript-skill | YouTube视频转录提取 | YouTube视频转录提取，字幕和摘要生成。Use when extracting YouTube transcripts, getting subtitles, or when user mentions "YouTube", "transcript", "subtitle", "video" |
| elevenlabs-skill | ElevenLabs TTS语音合成 | ElevenLabs TTS语音合成，文本转语音和声音克隆。Use when converting text to speech, generating audio, or when user mentions "TTS", "voice", "speech", "ElevenLabs" |

---

## Out of Scope 模板

每个 Skill 应该在 SKILL.md 中添加：

```markdown
## Out of Scope / 不适用范围

本 Skill **不** 处理以下情况：

- [不适合的任务1]（建议使用 [替代Skill]）
- [不适合的任务2]（建议使用 [替代Skill]）
- [不适合的任务3]

如果您需要以上功能，请考虑使用其他专门的 Skill。
```

---

## 优化示例

### 优化前：docx-skill

**skill.json:**
```json
{
  "description": "创建、编辑、格式化Word文档(.docx)，支持模板、表格、图片插入和文档合并"
}
```

**SKILL.md:**
缺少 "何时使用" 和 "Out of Scope"

---

### 优化后：docx-skill

**skill.json:**
```json
{
  "description": "创建、编辑、格式化Word文档(.docx)，支持模板、表格、图片插入和文档合并。Use when working with Word documents, creating reports, generating documents from templates, or when user mentions \"docx\", \"Word\", \"document\", \"report\", \"template\""
}
```

**SKILL.md 新增章节:**

```markdown
## 何时使用本 Skill

Use this skill when:
- 需要创建新的 Word 文档
- 需要编辑现有的 .docx 文件
- 从 Markdown/JSON 生成 Word 文档
- 使用模板批量生成文档
- 合并多个 Word 文档
- 提取或修改文档内容

触发关键词："docx", "Word", "document", "report", "template", "merge"

## Out of Scope / 不适用范围

本 Skill **不** 处理以下情况：

- 处理 .doc 格式（旧版 Word）- 请先将文件转换为 .docx
- OCR 扫描文档的文字识别 - 请使用 pdf-skill 或专门的 OCR 工具
- 复杂的宏或 VBA 脚本 - 本 Skill 专注于文档内容处理
- 密码保护的文档 - 请先移除密码保护
- 实时协作编辑 - 本 Skill 处理的是本地文件操作

如果您需要以上功能，请考虑使用其他专门的工具或 Skill。
```

---

## 批量优化命令

使用 skill-creator-enhanced 来验证和升级现有 Skills：

```bash
# 验证所有 Skills
for skill in */; do
  kimi skill run skill-creator-enhanced --params "action=validate&skill_path=$skill"
done

# 批量升级（添加缺失的标准文件）
for skill in */; do
  kimi skill run skill-creator-enhanced --params "action=upgrade&skill_path=$skill"
done
```

---

## 质量检查清单

优化后的每个 Skill 应该满足：

- [ ] description 包含 "Use when" 触发条件
- [ ] description 包含 5+ 个具体关键词
- [ ] description 少于 1024 字符
- [ ] SKILL.md 有 "何时使用" 章节
- [ ] SKILL.md 有 "Out of Scope" 章节
- [ ] 使用第三人称描述（无 "I"/"you"）
- [ ] 明确说明文件类型（.docx, .pdf, .xlsx 等）

---

*优化指南版本: 1.0*
*基于: Anthropic官方最佳实践 + 社区200+ Skills测试数据*
