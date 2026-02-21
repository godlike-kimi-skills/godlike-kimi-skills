# 🚀 GitHub 发布检查清单

> 本清单用于指导 Godlike Kimi Skills 项目发布到 GitHub 的完整流程

---

## ✅ 第一阶段：组织创建

### 1.1 创建 GitHub 组织
- [ ] 访问 https://github.com/account/organizations/new
- [ ] 组织名称: `godlike-kimi-skills` (或备选: `awesome-kimi-skills`)
- [ ] 联系邮箱: 填写您的邮箱
- [ ] 选择组织类型: Free (免费版)
- [ ] 点击 **Create organization**

### 1.2 完善组织信息
- [ ] 上传组织头像 (建议使用 🌙 月神主题 Logo)
- [ ] 填写组织描述: "全球首个中文 Kimi Code CLI Skills 生态系统"
- [ ] 设置组织网站: (可选)
- [ ] 配置讨论区 (Discussions): 开启

---

## ✅ 第二阶段：仓库准备

### 2.1 初始化 Git 仓库
```powershell
# 在项目根目录执行
cd D:\kimi\projects\godlike-kimi-skills
git init
git add .
git commit -m "🚀 Initial commit: 224+ production-ready skills for Kimi CLI"
git branch -M main
```

### 2.2 创建 GitHub 仓库
- [ ] 访问组织页面 → 点击 **New repository**
- [ ] 仓库名称: `godlike-kimi-skills`
- [ ] 描述: "🌙 月神技能 - 全球首个AI运营的中文Kimi Code CLI Skills生态系统，包含224+生产级技能"
- [ ] 可见性: **Public** (公开)
- [ ] 勾选: ☑️ Add a README file (自动生成)
- [ ] 点击 **Create repository**

### 2.3 推送代码到 GitHub
```powershell
# 添加远程仓库地址（根据实际创建的组织名修改）
git remote add origin https://github.com/godlike-kimi-skills/godlike-kimi-skills.git

# 推送主分支
git push -u origin main
```

**或者使用提供的推送脚本:**
```powershell
# 运行推送脚本
.\push-to-github.ps1
```

---

## ✅ 第三阶段：仓库配置

### 3.1 设置 Topics 标签
访问仓库主页 → 点击右侧 **About** → ⚙️ 设置 Topics：

```
kimi
kimi-cli
ai-tools
skills
awesome
chinese
developer-tools
productivity
automation
open-source
awesome-list
```

### 3.2 配置仓库详情
- [ ] **Website**: 填写项目主页（如有）
- [ ] **Topics**: 添加上述标签
- [ ] **Releases**: 确保启用
- [ ] **Packages**: 可选择性启用
- [ ] **Wiki**: 根据需要决定是否启用

### 3.3 保护主分支 (可选但推荐)
- [ ] Settings → Branches → Add rule
- [ ] Branch name pattern: `main`
- [ ] 勾选:
  - ☑️ Require pull request reviews before merging
  - ☑️ Require status checks to pass before merging
  - ☑️ Include administrators

---

## ✅ 第四阶段：Secrets 配置

### 4.1 访问 Secrets 设置
Settings → Secrets and variables → Actions

### 4.2 添加必要的 Secrets

| Secret 名称 | 用途 | 是否必需 |
|------------|------|---------|
| `GITHUB_TOKEN` | 自动生成，用于 Actions | 自动 |
| `DISCUSSION_WEBHOOK` | 讨论区通知 Webhook | 可选 |

### 4.3 添加环境变量 (可选)
Settings → Secrets and variables → Actions → Variables

| 变量名称 | 值 |
|---------|---|
| `DEFAULT_LANGUAGE` | `zh-CN` |
| `SKILL_COUNT` | `224` |

---

## ✅ 第五阶段：功能启用

### 5.1 Issues 配置
- [ ] Settings → Features → ☑️ Issues
- [ ] 设置 Issue templates (使用 `.github/ISSUE_TEMPLATE/`)

### 5.2 Discussions 配置
- [ ] Settings → Features → ☑️ Discussions
- [ ] 设置讨论分类:
  - 🙏 Q&A (提问)
  - 💡 Ideas (想法)
  - 🐞 Bug Reports (Bug反馈)
  - 📣 Announcements (公告)

### 5.3 Projects (看板)
- [ ] 创建项目看板用于追踪开发进度

---

## ✅ 第六阶段：发布首版 Release

### 6.1 创建标签
```bash
# 创建 v1.0.0 标签
git tag -a v1.0.0 -m "🎉 v1.0.0 - 首次发布，包含224+ Skills"
git push origin v1.0.0
```

### 6.2 发布 Release
- [ ] 仓库主页 → Releases → **Draft a new release**
- [ ] Choose a tag: `v1.0.0`
- [ ] Release title: `🌙 v1.0.0 - 月神初临`
- [ ] 描述模板:

```markdown
## 🎉 首次正式发布

### 📊 数据统计
- **总 Skills 数量**: 224+
- **质量等级分布**:
  - 🏆 金印 (AAA): XX 个
  - 🥈 银牌 (AA): XX 个
  - 🥉 铜牌 (A): XX 个

### ✨ 核心特性
- 全球首个AI运营的中文Kimi Code CLI Skills生态系统
- 7大分类：开发、AI、思维、效率、安全、金融、文化
- 100%中文文档与示例
- 5级质量评级体系

### 📚 快速开始
```bash
# 安装Skill
kimi skill install https://github.com/godlike-kimi-skills/skill-creator-enhanced

# 使用Skill
kimi skill run skill-creator-enhanced
```

### 🙏 致谢
感谢所有贡献者！
```

- [ ] 上传附件 (可选)
- [ ] 勾选 ☑️ Set as a pre-release (如果是预发布)
- [ ] 点击 **Publish release**

---

## ✅ 第七阶段：社区推广

### 7.1 社交媒体
- [ ] 在 Twitter/X 发布项目上线公告
- [ ] 在相关技术社区发帖 (V2EX、掘金、知乎等)
- [ ] 发送 Newsletter 给关注者

### 7.2 技术社区
- [ ] 提交到 [awesome-awesomeness](https://github.com/bayandin/awesome-awesomeness)
- [ ] 提交到 [awesome](https://github.com/sindresorhus/awesome) (需符合标准)
- [ ] 在 Reddit r/selfhosted 分享

### 7.3 文档完善
- [ ] 确认所有链接有效
- [ ] 更新 CHANGELOG.md
- [ ] 更新贡献者列表

---

## 📋 验证清单

发布前最后检查：

- [ ] 所有文件已推送到 GitHub
- [ ] README.md 显示正常
- [ ] 所有图片/徽章可正常加载
- [ ] 所有链接可正常访问
- [ ] Release 已发布
- [ ] Topics 已设置
- [ ] Issues/Discussions 已启用

---

## 🆘 故障排除

### 推送失败
```powershell
# 如果远程已存在，先删除再添加
git remote remove origin
git remote add origin https://github.com/godlike-kimi-skills/godlike-kimi-skills.git
git push -u origin main --force  # ⚠️ 谨慎使用强制推送
```

### 权限问题
- 确认 GitHub 账号有组织的写入权限
- 检查是否配置了正确的 Git 凭据

---

**完成时间**: ___年___月___日  
**负责人**: _______________
