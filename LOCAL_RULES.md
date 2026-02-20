# 本地项目规则 / Local Project Rules

> 🔒 **本文档仅限内部使用，禁止对外公开**  
> 📅 **生效日期:** 2026-02-20  
> 🎯 **适用范围:** Godlike Kimi Skills 项目全体成员

---

## 一、静默建设期核心规则 (Week 1)

### 1.1 对外沟通禁令 / Communication Ban

**🚫 绝对禁止 (零容忍):**

| 禁止事项 | 说明 | 违规后果 |
|----------|------|----------|
| **联系Kimi官方** | 包括邮件、社交媒体、GitHub issue、Slack等所有渠道 | 破坏静默期战略 |
| **社区公开发布** | V2EX、掘金、知乎、微博、Twitter、Reddit等 | 提前暴露，失去先发优势 |
| **竞对仓库活跃** | 在OpenClaw、awesome-openclaw等仓库提issue/PR | 引起竞对警觉 |
| **透露精确数据** | 当前skills数量、运营策略、商业计划细节 | 信息泄露风险 |
| **对外身份发言** | 以项目名义在任何公开场合发言 | 不可控风险 |

**✅ 允许事项:**

- GitHub正常代码提交 (保持低调)
- 本地开发和测试
- 内部文档完善
- 准备发布材料 (暂不发)

### 1.2 信息保密等级 / Information Classification

**🔴 绝密 (绝对禁止外泄):**
- 当前精确的skills数量
- 详细的运营数据和策略
- 商业计划书完整内容
- 与竞对的详细对比分析
- 联系Kimi官方的具体方案

**🟡 机密 (谨慎处理):**
- 质量认证的详细评分标准
- 自动化工具的实现细节
- 批量生成skills的方法
- 内部时间规划和里程碑

**🟢 公开 (可对外):**
- 项目存在本身 (GitHub公开)
- 通用的开发规范
- 开源的代码和文档
- 项目愿景和大方向

**对外统一话术:**
> "我们正在建设全球最大的中文Kimi Skills仓库，具体数据敬请期待一周后的正式发布。"

---

## 二、Skills开发规则 / Skills Development Rules

### 2.1 批量创建优先级

```
优先级1 (高): 移植竞对热门skills
├── 从OpenClaw ClawHub移植热门skills
├── 本地化为中文场景
├── 改进质量和文档
└── 目标: 40个

优先级2 (中): 生成通用工具类skills
├── 文件处理类 (批量重命名、格式转换等)
├── 数据处理类 (CSV/JSON/Excel处理)
├── 系统工具类 (监控、清理、备份等)
└── 目标: 50个

优先级3 (中): 填充细分赛道
├── 每个细分赛道至少3个skills
├── 覆盖高频使用场景
├── 避免同质化竞争
└── 目标: 20个
```

### 2.2 质量标准底线

**所有新skills必须通过质量检查:**

| 等级 | 分数 | 要求 | 处理 |
|------|------|------|------|
| **AAA** | 95-100 | 完美 | 首页推荐 |
| **AA** | 80-94 | 优秀 | 正常收录 |
| **A** | 60-79 | 良好 | 正常收录 |
| **B** | 40-59 | 合格 | 需改进提示 |
| **C** | <40 | 不合格 | 拒绝收录 |

**静默期目标:**
- 所有新skills达到A级 (≥60分)
- 核心skills达到AA级 (≥80分)
- 争取2-3个AAA级标杆skills

### 2.3 文档规范检查清单

**每个SKILL.md必须包含:**

- [ ] 双语描述 (中文在前)
- [ ] 功能特性列表 (至少3项)
- [ ] 安装说明 (CLI + 手动)
- [ ] 使用示例 (至少2个)
- [ ] 参数说明表格
- [ ] 常见问题FAQ (至少2个)
- [ ] 更新日志
- [ ] 许可证声明

---

## 三、代码提交规则 / Commit Rules

### 3.1 提交信息格式

```
<类型>: <中文描述> / <English description>

<详细中文说明>
<Detailed English description>

- 变更点1 / Change 1
- 变更点2 / Change 2

静默期 / Stealth: Week 1 Day X
```

### 3.2 类型定义

| 类型 | 用途 | 示例 |
|------|------|------|
| `feat` | 新增skill或功能 | feat: 添加文件批量重命名skill |
| `fix` | 修复bug | fix: 修复路径兼容性问题 |
| `docs` | 文档更新 | docs: 完善SKILL.md双语描述 |
| `refactor` | 代码重构 | refactor: 优化代码结构 |
| `test` | 测试相关 | test: 添加单元测试 |
| `chore` | 工具/配置 | chore: 更新CI配置 |

### 3.3 提交频率

**最低要求:**
- 每日至少3次提交
- 每次提交聚焦单一目标
- 保持commit历史清晰可读

**推荐节奏:**
- 上午: 1-2次提交 (新skills/功能)
- 下午: 1-2次提交 (文档/测试/工具)
- 晚上: 0-1次提交 (修复/优化)

---

## 四、本地开发流程 / Local Development Workflow

### 4.1 标准开发流程

```bash
# 1. 创建新skill
cd templates/skill-template
cp -r . ../../skills/my-new-skill
cd ../../skills/my-new-skill

# 2. 编辑SKILL.md和代码
# ... 编辑文件 ...

# 3. 本地测试
python scripts/main.py --help
python scripts/main.py --test

# 4. 质量检查
python ../../tools/quality-check/quality-check.py .

# 5. 提交
cd ../..
git add skills/my-new-skill
git commit -m "feat: 添加XXX skill / Add XXX skill

详细描述

静默期 / Stealth: Week 1 Day X"

# 6. 推送 (本地仓库)
git push origin main
```

### 4.2 质量检查流程

**每次提交前必须执行:**

```bash
# 进入skill目录
cd skills/your-skill

# 运行质量检查
python ../../tools/quality-check/quality-check.py .

# 查看报告
cat quality-report.json

# 确保分数≥60 (A级)
```

**质量检查未通过的处理:**
1. 查看质量报告中的具体问题
2. 按建议改进
3. 重新运行检查
4. 直到达到目标等级

---

## 五、数据管理规则 / Data Management

### 5.1 Git忽略规则

**必须加入.gitignore的:**
```
# 敏感信息
.env
.env.local
*.key
*.token
*.secret

# 临时文件
.tmp/
temp/
*.tmp

# 质量报告 (本地生成)
quality-report.json

# IDE配置
.vscode/
.idea/
```

### 5.2 数据备份

**每日备份:**
- GitHub仓库自动备份
- 本地定期push到origin

**关键文档备份:**
- 商业计划书: 本地加密 + 云盘
- 运营数据: GitHub私有repo

---

## 六、违规处理 / Violation Handling

### 6.1 违规行为定义

**严重违规 (立即处理):**
- 对外泄露绝密信息
- 违反静默期禁令联系外部
- 故意破坏项目规则

**一般违规 (警告整改):**
- 提交质量不达标的skills
- 文档不符合规范
- 未按流程执行

### 6.2 处理措施

**严重违规:**
- 立即停止相关操作
- 评估损失和影响
- 制定补救措施

**一般违规:**
- 书面警告
- 限期整改
- 复查确认

---

## 七、规则更新 / Rule Updates

### 7.1 更新流程

1. 提出规则修改建议
2. 内部讨论评估
3. 更新LOCAL_RULES.md
4. 同步给所有成员
5. 记录变更日志

### 7.2 变更日志

| 日期 | 版本 | 变更内容 | 变更人 |
|------|------|----------|--------|
| 2026-02-20 | v1.0 | 初始版本 | AI Agent |

---

## 八、签署确认 / Acknowledgment

**本人已阅读并同意遵守以上所有规则:**

> 我承诺在静默建设期内:
> - 不对外联系Kimi官方
> - 不在社区公开发布
> - 不泄露项目敏感信息
> - 严格按照规范执行
> - 专注于内功修炼

**签署人:** _______________  
**日期:** 2026-02-20

---

**本文档为内部机密，未经授权不得外传。**
