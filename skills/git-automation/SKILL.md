# Git Automation

**生产级Git工作流自动化** - 借鉴 Git Flow, GitHub Flow, Trunk-Based Development

自动建仓、智能提交、分支管理、代码审查、CI/CD集成。

---

## 核心特性

### 🌿 分支策略 (Git Flow)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   main      │←────│  develop    │←────│ feature/*   │
│  (生产)     │     │  (开发)     │     │  (功能)     │
└──────┬──────┘     └──────┬──────┘     └─────────────┘
       │                   │
       │            ┌──────┴──────┐
       │            │ release/*   │
       │            │  (发布)     │
       │            └──────┬──────┘
       │                   │
       │            ┌──────┴──────┐
       └────────────│ hotfix/*    │
                    │  (热修复)   │
                    └─────────────┘
```

### 🔄 工作流对比

| 工作流 | 分支模型 | 适用场景 |
|--------|----------|----------|
| **Git Flow** | main + develop + feature/release/hotfix | 大型项目，发布周期明确 |
| **GitHub Flow** | main + feature + PR | 持续部署，快速迭代 |
| **Trunk-Based** | main + short-lived feature | 超大型项目，高频集成 |

---

## 使用方法

### 初始化项目
```bash
# 自动建仓 (GitHub + Git初始化)
git-auto init my-project --private --template=python

# 使用Git Flow初始化
git-auto init my-project --flow=gitflow
```

### 智能提交
```bash
# 分析变更并生成提交信息
git-auto commit --analyze

# 规范提交 (Conventional Commits)
git-auto commit --type=feat --scope=api --message="add user auth"
```

### 分支管理
```bash
# 创建功能分支
git-auto feature start user-authentication

# 完成功能并合并
git-auto feature finish user-authentication

# 创建发布分支
git-auto release start 1.0.0

# 热修复
git-auto hotfix start security-patch
```

### 代码审查
```bash
# 创建PR
git-auto pr create --title="Feature: User Auth" --reviewers=alice,bob

# 检查PR状态
git-auto pr status

# 合并PR
git-auto pr merge --squash
```

---

## 质量保障体系

基于PDCA循环、精益思想、约束理论、六西格玛和持续改进框架，建立可靠的Git工作流质量保障体系。

### 质量目标

| 指标 | 目标值 | 测量方法 |
|-----|--------|---------|
| 操作成功率 | >99.9% | 操作日志统计 |
| 提交规范率 | 100% | 提交信息检查 |
| 合并冲突率 | <5% | PR合并统计 |
| 代码审查周期 | <24小时 | PR在审时间 |
| 发布频率 | >2次/周 | 发布记录 |

### PDCA质量循环

```
Plan (计划)
├── 工作流选择 (Git Flow/GitHub Flow/Trunk)
├── 分支策略定义
├── 质量门禁设计
├── 权限模型规划
└── 风险预案制定
        ↓
Do (执行)
├── 本地验证
├── 分支操作
├── PR创建与审查
├── 合并发布
└── 监控记录
        ↓
Check (检查)
├── 操作结果验证
├── 代码质量检查
├── CI/CD状态确认
├── 分支健康检查
└── 流程合规审计
        ↓
Act (处理)
├── 问题修复
├── 流程优化
├── 规范更新
└── 知识分享
```

### 精益Git工作流

**浪费识别**:  
| 浪费类型 | 表现 | 消除措施 |
|---------|------|---------|
| 等待 | PR审查等待 | 审查SLA+自动提醒 |
| 库存 | 未合并分支堆积 | WIP限制 |
| 缺陷 | 合并冲突 | 定期rebase |
| 过度加工 | 过度详细的提交 | 平衡规范与效率 |
| 动作 | 重复git命令 | 自动化脚本 |

**看板应用于PR管理**:  
```
[Backlog] → [In Review] → [Changes Requested] → [Approved] → [Merged]
   [WIP:5]      [WIP:3]          [WIP:2]           [WIP:3]     [WIP:∞]
```

### 约束管理

**系统约束识别**:  
1. 代码审查能力（审查者时间）
2. CI/CD资源
3. 发布窗口
4. 合并权限

**挖尽约束**:  
- 自动化代码检查减少审查负担
- 并行测试提高CI效率
- 特性开关解耦发布
- 信任机制扩大合并权限

**DBR调度**:  
- **鼓**: 以代码审查吞吐量为节拍
- **缓冲**: 维护审查队列，设置SLA
- **绳**: WIP限制控制新PR创建

### 六西格玛质量门禁

**提交前检查 (Pre-commit)**:  
```bash
# Git钩子检查清单
✓ 代码格式化检查 (black/prettier)
✓ 代码风格检查 (flake8/eslint)
✓ 单元测试通过
✓ 提交信息格式检查
✓ 敏感信息扫描
```

**PR合并门禁**:  
```
必需检查:
├── CI构建通过
├── 代码审查通过 (至少1人)
├── 分支已更新到最新
├── 无冲突
└── 符合分支策略
```

**质量度量**:  
```python
from git_automation import Metrics

metrics = Metrics()
metrics.track_pr_lifecycle()       # PR生命周期
metrics.track_review_time()        # 审查时间
metrics.track_merge_conflict()     # 合并冲突率
metrics.track_branch_health()      # 分支健康度
metrics.generate_dashboard()       # 生成仪表板
```

### 持续改进

**Kaizen改进循环**:  
1. **收集**: 收集团队反馈和痛点
2. **分析**: 分析Git工作流度量数据
3. **改进**: 实施流程优化
4. **验证**: 验证改进效果
5. **标准化**: 将有效实践固化为规范

**定期回顾会议**:  
- 每周: 审查PR积压情况
- 每月: Git工作流效果评估
- 每季度: 分支策略审查

### 安全检查清单

**分支操作前**:  
- [ ] 工作区是否干净? (git status)
- [ ] 是否已拉取最新代码? (git pull)
- [ ] 目标分支是否正确?
- [ ] 是否有未提交的更改?

**合并前**:  
- [ ] CI是否全部通过?
- [ ] 是否已解决所有冲突?
- [ ] 是否经过代码审查?
- [ ] 是否已测试关键功能?

**发布前**:  
- [ ] 版本号是否正确?
- [ ] CHANGELOG是否已更新?
- [ ] 是否已打标签?
- [ ] 回滚方案是否就绪?

### Git钩子配置

```bash
#!/bin/sh
# .git/hooks/pre-commit

# 代码格式化检查
echo "检查代码格式..."
black --check .
if [ $? -ne 0 ]; then
    echo "❌ 代码格式检查失败，请运行 'black .' 修复"
    exit 1
fi

# 提交信息检查
commit_msg_file=$1
commit_msg=$(cat $commit_msg_file)

if ! echo "$commit_msg" | grep -qE "^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+"; then
    echo "❌ 提交信息格式错误，请使用 Conventional Commits 格式"
    exit 1
fi

echo "✅ 预提交检查通过"
exit 0
```

### 风险管理

**风险矩阵**:  
| 风险 | 概率 | 影响 | 缓解措施 |
|-----|------|------|---------|
| 强制推送丢失代码 | 中 | 高 | 禁止直接推main，强制Git钩子 |
| 错误合并 | 中 | 高 | 强制PR+审查+CI |
| 分支漂移 | 高 | 中 | 定期rebase提醒 |
| 发布失败 | 低 | 高 | 自动化回滚机制 |

### 工作流选择决策树

```
是否需要版本发布?
├── No → 使用 GitHub Flow
│         └── main + feature分支，持续部署
│
└── Yes → 发布频率?
    ├── 每天多次 → Trunk-Based Development
    │               └── main + 短期feature分支
    │
    ├── 每周/每两周 → GitHub Flow
    │                 └── 简化流程，标签发布
    │
    └── 每月或更长 → Git Flow
                    └── main + develop + feature/release/hotfix
```

---

## 参考实现

### 开源工具
- **git-flow**: https://github.com/nvie/gitflow
- **GitHub CLI**: https://cli.github.com/
- **semantic-release**: 自动化版本管理

### 最佳实践
- **Conventional Commits**: 规范提交信息
- **Semantic Versioning**: 语义化版本
- **GitHub Flow**: 简单分支模型

---

## 版本信息

- **Version**: 2.0.0
- **Author**: KbotGenesis
- **References**: Git Flow, GitHub Flow, Conventional Commits
- **Quality Report**: 参见 QUALITY_ANALYSIS_REPORT.md
