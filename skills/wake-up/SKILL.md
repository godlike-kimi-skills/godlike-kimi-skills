# Wake Up

**系统唤醒与初始化** - Official Native Skill for Kimi CLI

执行完整的系统唤醒流程，确保所有组件就绪并同步最新状态。

---

## 执行流程

当用户说 **"wake up"** 或 **"启动系统"** 时，执行以下流程：

```
┌─────────────────────────────────────────────────────────┐
│  1. SYSTEM HEALTH CHECK                                 │
│     检查系统健康状态                                     │
│     - 检查磁盘空间                                       │
│     - 检查内存使用                                       │
│     - 检查网络连接                                       │
│     - 检查GitHub连接                                     │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  2. BACKUP VERIFICATION                                 │
│     验证备份系统状态                                     │
│     - 检查最新备份                                       │
│     - 验证备份完整性                                     │
│     - 如有必要，执行一键备份                             │
│     → 调用 one-click-backup skill                       │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  3. MEMORY LOADING                                      │
│     加载所有记忆系统                                     │
│     - 加载Hot Memory (P0)                                │
│     - 加载Warm Memory (P1/P2)                            │
│     - 恢复活跃Channel                                    │
│     - 同步Memory Blocks                                  │
│     → 调用 memory-directory-manager                     │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  4. D:/KIMI WORKSPACE SYNC                              │
│     同步Kbot工作区关键信息                               │
│     - 读取D:/kimi记忆目录统计                            │
│     - 检查SmartBackups最新备份                           │
│     - 统计skills目录（总数/新增/更新）                   │
│     - 读取关键项目状态                                   │
│     - 检查business-memory最新规则                        │
│     → 生成工作区状态摘要                                 │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  5. AGENT SYNCHRONIZATION                               │
│     同步所有Agent状态                                    │
│     - 检查Agent Bus状态                                  │
│     - 读取最新备份通知                                   │
│     - 同步OpenClaw工作区                                 │
│     - 更新Agent注册表                                    │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  6. READY STATE                                         │
│     系统就绪                                             │
│     - 生成状态报告                                       │
│     - 显示可用命令                                       │
│     - 等待用户输入                                       │
└─────────────────────────────────────────────────────────┘
```

---

## 唤醒检查清单

### 系统检查
- [ ] 磁盘空间 > 10GB
- [ ] 内存可用 > 2GB
- [ ] 网络连接正常
- [ ] GitHub API 可达

### 备份检查
- [ ] 最新备份 < 24小时
- [ ] 备份完整性验证通过
- [ ] GitHub同步状态正常

### 记忆检查
- [ ] Hot Memory 加载成功
- [ ] Identity 配置有效
- [ ] Channel 状态恢复
- [ ] Memory Blocks 同步

### D:/Kimi 工作区检查
- [ ] D:/kimi 目录可访问
- [ ] 记忆目录统计完成
- [ ] SmartBackups检查完成
- [ ] Skills清单生成
- [ ] 关键项目状态读取

### Agent检查
- [ ] Agent Bus 运行正常
- [ ] 所有Agents已注册
- [ ] 消息队列无堆积

---

## Step 4 详细规范: D:/KIMI WORKSPACE SYNC

### 执行命令

```powershell
# 1. 检查D:/kimi目录结构和大小
Get-ChildItem D:\kimi -Directory | Select-Object Name, @{Name="Size(MB)";Expression={[math]::Round((Get-ChildItem $_.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum/1MB,2)}}

# 2. 读取记忆目录统计
$memoryDirs = @("hot","warm","cold")
foreach ($dir in $memoryDirs) {
    $path = "D:\kimi\memory\$dir"
    if (Test-Path $path) {
        $count = (Get-ChildItem $path -Recurse -File -ErrorAction SilentlyContinue).Count
        $size = (Get-ChildItem $path -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        Write-Host "  [OK] $dir`: $count files, $([math]::Round($size/1KB,2)) KB"
    }
}

# 3. 检查SmartBackups最新备份
$backupDir = "D:\kimi\SmartBackups"
if (Test-Path $backupDir) {
    $latest = Get-ChildItem $backupDir -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($latest) {
        $backupSize = (Get-ChildItem $latest.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        $hoursAgo = [math]::Round(((Get-Date) - $latest.LastWriteTime).TotalHours, 1)
        Write-Host "  [OK] Latest: $($latest.Name), $([math]::Round($backupSize/1MB,2)) MB, ${hoursAgo}h ago"
    }
}

# 4. 统计skills
$skillsDir = "D:\kimi\skills"
if (Test-Path $skillsDir) {
    $skillCount = (Get-ChildItem $skillsDir -Directory).Count
    Write-Host "  [OK] Skills: $skillCount total"
}

# 5. 检查关键项目
$projects = @("winsage-evolution","godlike-kimicode-skills","auto-service")
foreach ($proj in $projects) {
    $projPath = "D:\kimi\projects\$proj"
    if (Test-Path $projPath) {
        Write-Host "  [OK] Project: $proj"
    }
}

# 6. 检查business-memory关键文件
$bizFiles = @("BUSINESS-RULES.md","winsage-redo-playbook.md","STRATEGIC-GOAL-ANALYSIS.md")
foreach ($file in $bizFiles) {
    $filePath = "D:\kimi\business-memory\$file"
    if (Test-Path $filePath) {
        $lastMod = (Get-Item $filePath).LastWriteTime
        Write-Host "  [OK] $file (modified: $lastMod)"
    }
}
```

### 输出示例

```
[Step 4/6] D:/Kimi Workspace Sync...
  [OK] Memory Structure:
       hot: 2 files, 0.75 KB
       warm: 3 files, 0.77 KB
       cold: 0 files, 0 KB
  [OK] SmartBackups: FULL-20260220-082239, 53.38 MB, 0.8h ago
  [OK] Skills: 90 total
  [OK] Projects: winsage-evolution, godlike-kimicode-skills
  [OK] Business Rules: v2.5 (ACTIVE)
  [OK] Key Files:
       BUSINESS-RULES.md (modified: 2026-02-19)
       winsage-redo-playbook.md (modified: 2026-02-19)
```

---

## 记忆系统集成

### 自动加载流程
```
wake-up
  ↓
memory-directory-manager.status()     [检查目录健康]
  ↓
memory-directory-manager.load_hot()   [加载P0/P1记忆]
  ↓
long-term-memory.sync()               [同步向量索引]
  ↓
knowledge-graph.refresh()             [刷新关系图谱]
  ↓
系统就绪
```

### 启动时自动执行
```bash
# 检查记忆系统健康
memory-directory-manager health

# 显示当前记忆统计
memory-directory-manager stats

# 如有过期内容，提示归档
memory-directory-manager archive --dry-run
```

---

## 错误处理与恢复

### 阶段失败处理

| 失败阶段 | 处理策略 | 回退操作 |
|----------|----------|----------|
| Health Check | 跳过非关键检查 | 标记状态，继续 |
| Backup Verification | 强制备份 | 创建紧急备份 |
| Memory Loading | 从备份恢复 | 回退到默认配置 |
| D:/Kimi Workspace Sync | 记录错误 | 使用缓存信息 |
| Agent Sync | 延迟同步 | 标记离线，稍后重试 |

### 重试机制
```
失败 → 指数退避(1s, 2s, 4s, 8s) → 最多3次 → 标记异常
```

---

## 监控与反馈循环

### 运行时监控
```
┌─────────────┐
│ Wake Cycle  │
│  (每隔1h)   │
└──────┬──────┘
       ↓
┌─────────────────────┐
│ Health Check Loop   │
│ - 系统资源          │
│ - Agent状态         │
│ - 任务队列          │
└──────┬──────────────┘
       ↓
┌─────────────────────┐
│ 异常? → Alert       │
│ 正常? → Continue    │
└─────────────────────┘
```

### 关键指标追踪
- 启动时间
- 各阶段成功率
- 资源使用趋势
- 错误频率
- D:/kimi工作区变化检测

---

## 使用方式

### 基本唤醒
```
wake up
```
或
```
启动系统
```

### 快速唤醒（跳过备份检查和工作区同步）
```
wake up --quick
```

### 强制刷新（重新加载所有记忆和工作区）
```
wake up --refresh
```

### 诊断模式（显示详细检查过程）
```
wake up --diagnostic
```

### 仅工作区同步
```
wake up --workspace-only
```

---

## 输出示例

```
═══════════════════════════════════════════════════════════
                 Kbot Wake Up Sequence v1.2
═══════════════════════════════════════════════════════════

[Step 1/6] System Health Check...
  [OK] Disk space: 79GB available
  [OK] Memory: 15.7GB available
  [OK] Network: Connected
  [OK] GitHub API: Reachable

[Step 2/6] Backup Verification...
  [OK] Latest backup: 2026-02-20 08:22:39
  [OK] Backup size: 53.38MB
  [OK] Integrity check: Passed
  [OK] GitHub sync: Up to date

[Step 3/6] Memory Loading...
  [OK] Hot Memory (P0): Loaded (2 files, 0.75KB)
  [OK] Warm Memory (P1): Loaded (3 files, 0.77KB)
  [OK] Identity: Valid
  [OK] Memory Blocks: 3 blocks synced

[Step 4/6] D:/Kimi Workspace Sync...
  [OK] Memory Structure: hot/0.75KB, warm/0.77KB, cold/0KB
  [OK] SmartBackups: FULL-20260220-082239, 53.38MB, 0.8h ago
  [OK] Skills: 90 total
  [OK] Projects: winsage-evolution, godlike-kimicode-skills, auto-service
  [OK] Business Rules: v2.5 (ACTIVE - Cambrian Speed)

[Step 5/6] Agent Synchronization...
  [OK] Agent Bus: Running
  [OK] Registered agents: 5
  [OK] Message queue: 0 pending

[Step 6/6] System Ready...

═══════════════════════════════════════════════════════════
                    SYSTEM READY
═══════════════════════════════════════════════════════════

Welcome back! 👋

Current Status:
  • Memory: Fully loaded (15.48 KB)
  • D:/Kimi: 90 skills, 6 projects, 53MB backup
  • Business Rules: v2.5 (10+3 concurrent projects)
  • Backup: Up to date (0.8 hours ago)
  • Agents: All synchronized

Quick Stats:
  ├── Skills: 90 total
  ├── Projects: 6 active
  ├── Research Reports: 17
  ├── Business Memory: 7 key files
  └── Latest Backup: FULL-20260220-082239

Available Commands:
  /sessions list    - View session history
  /plan             - Create implementation plan
  /backup           - Execute one-click backup
  /status           - Check system status

What would you like to do today?
```

---

## 学习科学深度分析

### 🧠 间隔重复 (Spaced Repetition) 视角

Wake Up Skill 是间隔重复原理在**系统初始化领域**的创新应用。每次唤醒过程都是一次精心设计的"记忆激活"练习——系统不是简单地从冷启动加载，而是按照科学的时间间隔渐进式恢复记忆状态。

**渐进式记忆加载的科学性**：
唤醒流程的六个阶段（Health Check → Backup → Memory Loading → Workspace Sync → Agent Sync → Ready）对应记忆的六个激活层级：
1. **环境检查**：激活外部环境记忆（磁盘、网络状态）
2. **备份验证**：激活数据安全记忆（历史状态确认）
3. **记忆加载**：激活工作记忆（P0/P1/P2分级恢复）
4. **工作区同步**：激活项目上下文（D:/kimi最新状态）
5. **Agent同步**：激活社交/协作记忆（多Agent状态）
6. **就绪状态**：激活任务记忆（可用命令、上下文）

这种分层激活模仿了间隔重复中的"渐进提示"——从最容易恢复的信息开始，逐步唤醒更复杂的记忆网络。

**间隔效应在系统设计中的体现**：
- `--quick`模式跳过备份检查，对应短期记忆的快速恢复
- `--refresh`模式强制重新加载，对应长间隔后的全面复习
- `--workspace-only`模式专注工作区，对应特定上下文恢复
- 定期的Health Check Loop（每小时）对应间隔重复中的"复习节点"

**改进建议**：引入"记忆热度感知唤醒"——根据上次唤醒时间动态调整加载策略。如果距离上次唤醒不到1小时，采用热启动（仅恢复P0记忆）；如果超过24小时，采用全面刷新（P0+P1+P2+工作区检查）。这与间隔重复中的"间隔自适应"算法一致，优化了启动效率。

### 🎯 刻意练习 (Deliberate Practice) 视角

Wake Up 流程本身就是一套精心设计的刻意练习程序——它让用户和AI系统都在**学习区**内进行能力热身。

**唤醒作为能力诊断**：
系统健康检查不仅是技术检查，更是能力基线的测量。磁盘空间、内存可用性、网络延迟——这些指标反映了系统的"学习状态"。就像运动员在比赛前进行热身测试，唤醒流程让AI在进入正式任务前确认自己处于最佳状态。

**分阶段渐进式热身**：
唤醒流程的六个阶段对应刻意练习中的"任务分解"原则：
- **阶段1**：确认基础环境（类似运动员检查装备）
- **阶段2**：确认数据安全（类似回顾战术手册）
- **阶段3**：激活核心记忆（类似肌肉热身）
- **阶段4**：同步工作区上下文（类似场地熟悉）
- **阶段5**：同步协作能力（类似团队配合演练）
- **阶段6**：进入实战状态（类似比赛开始）

**诊断模式的刻意练习价值**：
`--diagnostic`模式是刻意练习的精髓体现——它不仅执行唤醒，还展示详细的思考过程。这类似于运动员观看自己的训练录像，帮助理解每个环节的作用和优化空间。

**改进建议**：开发"唤醒优化训练"模式，记录每次唤醒的时间和成功率，识别瓶颈环节并提供改进建议（如"您的Agent同步阶段平均耗时8秒，建议检查网络连接"）。引入"唤醒挑战"——模拟各种故障场景（备份损坏、网络中断），训练用户在压力下的恢复能力。

### 🔄 迁移学习 (Transfer Learning) 视角

Wake Up Skill 展示了强大的迁移学习能力——它将人类的晨间例行程序、计算机的启动序列、以及认知科学的状态恢复研究迁移到AI系统初始化场景。

**跨领域迁移的映射**：
- **人类晨间例行**：Wake Up 模仿人类醒来后的"热身"过程——先感知环境（Health Check），再确认安全（Backup），最后激活认知（Memory Loading + Workspace Sync）
- **操作系统启动**：借鉴Linux的init系统、Windows的服务管理，实现模块化、可并行的启动流程
- **认知状态恢复**：基于认知科学中的"情境依赖记忆"理论，通过恢复环境上下文帮助AI快速进入工作状态

**快速迁移的机制**：
系统的Channel切换支持（`channel_switch`事件触发备份）实现了工作状态的快速迁移。用户可以从"数据分析模式"切换到"代码开发模式"，系统保存当前上下文并加载新的配置，这对应迁移学习中的"快速适应新任务"。

**改进建议**：建立"场景模板库"，收录不同工作场景的唤醒配置（如"深度编码模式"加载coding-agent、dev-efficiency、git-automation；"研究分析模式"加载tavily、market-research、knowledge-graph）。引入"个人习惯学习"，根据用户的唤醒时间、常用Channel、优先任务自动优化唤醒流程。

### 🎓 元认知 (Metacognition) 视角

Wake Up 是元认知能力的外化——它让AI系统能够"思考自己的状态"、"评估自己的能力"、"监控自己的健康"。

**系统自我认知的层次**：
1. **感知层**（Health Check）：我知道我的环境状态
2. **记忆层**（Memory Loading）：我知道我记得什么
3. **工作区层**（Workspace Sync）：我知道我的项目状态
4. **能力层**（Agent Sync）：我知道我能做什么
5. **反思层**（状态报告）：我知道我刚才做了什么

这种分层自我认知对应元认知理论中的"元认知知识"（metacognitive knowledge）——关于自身认知过程的认知。

**监控-评估-调整的循环**：
唤醒流程中的Health Check Loop（每小时）和错误恢复机制构成了完整的元认知监控循环：
- **监控**：持续追踪系统指标
- **评估**：判断是否异常
- **调整**：执行恢复策略或发出警报

**改进建议**：引入"唤醒元报告"——不仅展示状态，还解释"为什么需要这个检查"（"检查GitHub连接是因为您的配置依赖远程技能同步"）。开发"认知负荷仪表盘"，显示当前加载的记忆量、激活的技能数、待处理的任务队列，帮助用户和AI理解当前的"认知状态"。建立"预测性唤醒"——基于用户的日程和习惯，提前预热系统（如用户每天早上9点开始工作，系统在8:55自动执行轻量唤醒）。

### 🌱 成长思维 (Growth Mindset) 视角

Wake Up 的设计哲学完全基于成长思维——它假设系统可以通过每次启动不断优化，而非固定不变。

**持续改进的证据**：
- **版本演进**：Wake Up v1.0只是起点，未来会有v2.0、v3.0，每次唤醒流程都可以迭代优化
- **失败即学习**：错误处理策略（指数退避、降级恢复）将故障转化为改进数据
- **适应性增强**：`--quick`、`--refresh`、`--diagnostic`等不同模式体现了"根据情境灵活调整"的成长思维

**挑战拥抱的设计**：
唤醒流程面对各种不确定性（网络波动、存储变化、配置更新），但设计选择了积极应对而非保守回避。这对应成长思维中的"拥抱挑战"特质。

**改进建议**：在状态报告中加入"成长指标"——显示本次唤醒比上次快了多少、新加载了哪些技能、修复了什么问题。设计"唤醒里程碑"系统，奖励连续成功唤醒、快速故障恢复等成就。建立"社区最佳实践分享"，让用户可以分享自己的唤醒配置和优化经验，形成集体智慧驱动的持续改进文化。

---

## 故障排除

### 唤醒失败时的处理

1. **系统检查失败**
   - 显示具体问题
   - 提供修复建议
   - 询问是否继续

2. **备份检查失败**
   - 自动执行一键备份
   - 或提示手动备份

3. **记忆加载失败**
   - 尝试从备份恢复
   - 或重新初始化

4. **D:/Kimi工作区同步失败**
   - 检查目录权限
   - 使用上次缓存的信息
   - 记录错误供后续排查

5. **Agent同步失败**
   - 重启Agent Bus
   - 重新注册Agents

---

## 学习增强配置

```yaml
wake_up_enhanced:
  # 间隔重复优化
  adaptive_wake:
    enabled: true
    hot_wake_threshold: 3600  # 1小时内热启动
    full_refresh_threshold: 86400  # 24小时后全面刷新
  
  # D:/kimi工作区同步配置
  workspace_sync:
    enabled: true
    check_memory: true
    check_backups: true
    check_skills: true
    check_projects: true
    check_business_rules: true
    cache_ttl: 300  # 5分钟缓存
  
  # 刻意练习模式
  practice_mode:
    enabled: false
    simulate_failures: false
    track_performance: true
    performance_history: 30  # 保留30天记录
  
  # 迁移学习支持
  scene_templates:
    - name: "deep_coding"
      skills: ["coding-agent", "dev-efficiency", "git-automation"]
    - name: "research_analysis"
      skills: ["tavily", "market-research", "knowledge-graph"]
    - name: "content_creation"
      skills: ["doc-gen-skill", "url-digest", "thinking-framework"]
    - name: "business_execution"
      skills: ["business-strategy", "project-planning", "wake-up"]
  
  # 元认知增强
  metacognitive_report:
    enabled: true
    explain_checks: true
    cognitive_load_display: true
  
  # 成长思维激励
  growth_tracking:
    enabled: true
    show_improvements: true
    milestone_badges: true
```

---

## 相关组件

| 组件 | 路径 | 用途 |
|------|------|------|
| **Health Check** | `security-check` | 系统健康检查 |
| **Backup** | `one-click-backup` | 备份验证和执行 |
| **Memory** | `memory-directory-manager` | 记忆加载 |
| **Workspace Sync** | `wake-up` (Step 4) | D:/kimi工作区同步 |
| **Agent Bus** | `agent-bus` | Agent同步 |
| **OpenClaw** | `.openclaw/workspace` | 工作区同步 |

---

## 参考来源

- **Linux Init System**: 操作系统启动序列
- **Cognitive State Recovery**: 认知状态恢复研究
- **Context-Dependent Memory**: 情境依赖记忆理论
- **Growth Mindset**: Carol Dweck成长型思维理论
- **Metacognition**: 元认知监控研究

---

## 版本信息

- **Version**: 1.2.0 (2026 D:/Kimi Workspace Sync 增强版)
- **Author**: KbotGenesis
- **Type**: Official Native
- **Trigger**: "wake up", "启动系统", "初始化"
- **Changelog**:
  - v1.2.0: 新增 Step 4 - D:/Kimi Workspace Sync
  - v1.1.0: 学习科学增强版
  - v1.0.0: 初始版本
