# 提交规范 / Commit Convention

> 🚨 **强制规则：所有提交必须使用中英文双语，中文在前**
>
> **Mandatory Rule: All commits must be bilingual, Chinese first**

---

## 📋 格式规范 / Format Specification

### 基本格式 / Basic Format

```
<类型>: <中文描述> / <English description>

<详细中文说明（可选）>
<Detailed English description (optional)>
```

### 单行示例 / Single Line Examples

```bash
# ✅ 正确 / Correct
feat: 添加股票预警功能 / Add stock alert feature
fix: 修复内存泄漏问题 / Fix memory leak issue
docs: 更新README安装说明 / Update README installation guide

# ❌ 错误 / Incorrect
feat: add stock alert feature          # 缺少中文 / Missing Chinese
feat: 添加股票预警功能                # 缺少英文 / Missing English
add stock alert feature                # 缺少类型和中文 / Missing type and Chinese
```

### 多行示例 / Multi-line Examples

```bash
feat: 添加微信通知支持 / Add WeChat notification support

添加微信公众号消息推送功能，支持模板消息
Add WeChat official account message push with template message support

- 支持多种消息模板 / Support multiple message templates
- 支持消息队列 / Support message queue
- 添加重试机制 / Add retry mechanism
```

---

## 🏷️ 提交类型 / Commit Types

| 类型 | 中文 | English | 用途 / Usage |
|------|------|---------|-------------|
| `feat` | 功能 | Feature | 新功能 / New feature |
| `fix` | 修复 | Bug Fix | 修复bug / Bug fix |
| `docs` | 文档 | Documentation | 仅文档更新 / Documentation only |
| `style` | 格式 | Code Style | 代码格式（不影响功能）/ Code style (no functional change) |
| `refactor` | 重构 | Refactoring | 代码重构 / Code refactoring |
| `perf` | 性能 | Performance | 性能优化 / Performance improvement |
| `test` | 测试 | Tests | 测试相关 / Tests related |
| `chore` | 构建 | Chores | 构建/工具相关 / Build/tool related |
| `ci` | 持续集成 | CI | CI/CD配置 / CI/CD configuration |
| `revert` | 回滚 | Revert | 回滚提交 / Revert commit |

---

## 📝 详细规则 / Detailed Rules

### 1. 标题行 / Title Line

- 必须以中文开头 / Must start with Chinese
- 中文后加空格和斜杠 / Add space and slash after Chinese
- 英文描述紧跟斜杠后 / English description follows the slash
- 总长度不超过72字符 / Max 72 characters total

```bash
# ✅ 正确
feat: 添加用户认证 / Add user authentication

# ❌ 过长 / Too long
feat: 添加一个非常长的功能描述，超过七十二个字符的限制 / Add a very long feature description that exceeds the seventy-two character limit
```

### 2. 正文 / Body

- 可选，用于详细说明 / Optional, for detailed explanation
- 必须双语 / Must be bilingual
- 中文段落在前 / Chinese paragraph first
- 英文段落紧跟 / English paragraph follows
- 使用空行分隔 / Use blank line to separate

### 3. 提交频率 / Commit Frequency

- 每个逻辑改动单独提交 / One logical change per commit
- 避免大而全的提交 / Avoid big-bang commits
- 及时提交，保持粒度小 / Commit frequently, keep small granularity

---

## 🔧 提交示例 / Commit Examples

### 添加Skill / Adding Skill

```bash
feat: 添加股票预警skill / Add stock alert skill

添加A股价格预警功能，支持微信通知和邮件提醒
Add A-share price alert with WeChat and email notifications

- 支持多股票监控 / Support multi-stock monitoring
- 支持自定义预警条件 / Support custom alert conditions
- 添加测试用例 / Add test cases
```

### 修复Bug / Fixing Bug

```bash
fix: 修复内存泄漏问题 / Fix memory leak issue

修复长期运行时的内存泄漏，释放未使用的缓存
Fix memory leak during long-running operations, release unused cache

Closes #123
```

### 更新文档 / Updating Documentation

```bash
docs: 更新README安装说明 / Update README installation guide

添加Windows安装步骤和常见问题解答
Add Windows installation steps and FAQ

- 添加截图说明 / Add screenshot instructions
- 添加视频教程链接 / Add video tutorial links
```

### 重构代码 / Refactoring

```bash
refactor: 重构数据库连接模块 / Refactor database connection module

提取数据库连接逻辑到独立模块，提高可测试性
Extract database connection logic to separate module for better testability

BREAKING CHANGE: 配置文件格式已更改 / Configuration file format changed
```

---

## ⚠️ 常见错误 / Common Mistakes

### ❌ 错误示例 / Wrong Examples

```bash
# 只有英文 / English only
feat: add new feature

# 只有中文 / Chinese only
feat: 添加新功能

# 顺序错误 / Wrong order
feat: Add feature / 添加新功能

# 缺少类型 / Missing type
添加新功能 / Add new feature

# 使用过去时 / Using past tense
feat: 添加了新功能 / Added new feature
```

### ✅ 正确示例 / Correct Examples

```bash
feat: 添加新功能 / Add new feature
fix: 修复登录问题 / Fix login issue
docs: 更新API文档 / Update API documentation
style: 格式化代码 / Format code
refactor: 优化查询逻辑 / Optimize query logic
perf: 提升加载速度 / Improve loading speed
test: 添加单元测试 / Add unit tests
chore: 更新依赖包 / Update dependencies
```

---

## 🛠️ 工具推荐 / Recommended Tools

### Git Hooks

使用 `commit-msg` hook 自动检查提交信息格式。

Use `commit-msg` hook to automatically check commit message format.

### IDE配置 / IDE Configuration

大多数IDE都支持提交模板配置，可以设置默认格式。

Most IDEs support commit template configuration.

---

## 📚 参考 / References

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Angular Commit Guidelines](https://github.com/angular/angular/blob/main/CONTRIBUTING.md#commit)

---

**让我们保持提交历史的清晰和专业！** 🚀  
**Let's keep the commit history clear and professional!** 🚀
