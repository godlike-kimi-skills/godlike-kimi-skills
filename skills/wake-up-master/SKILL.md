# Wake Up Master

**Kimi 完整系统唤醒与初始化** - Official Native Master Skill

整合所有Kimi唤醒相关功能的一体化解决方案，支持全局 `wake up` 命令调用。

---

## 快速使用

在全局状态下直接输入：

```bash
wake up              # 完整唤醒流程
wake up --quick      # 快速模式（跳过网络和更新检查）
wake up --update     # 专注Skills更新
wake up --security   # 专注安全检查
wake up --tasks      # 专注任务报告
```

---

## 执行逻辑总览（13阶段）

```
╔════════════════════════════════════════════════════════════════════╗
║                    WAKE UP MASTER SEQUENCE                         ║
║                    Total: 13 Phases | ~3-5 minutes                 ║
╚════════════════════════════════════════════════════════════════════╝

PHASE 1: SYSTEM HEALTH CHECK          [本地]  ~5s
├── 磁盘空间检测 (保留10GB+)
├── 内存状态检测 (保留2GB+)
├── CPU负载检测
├── 网络连接检测
└── 关键服务状态检查

PHASE 2: ENVIRONMENT VALIDATION       [本地]  ~3s
├── Kimi CLI配置检查
├── 必要目录结构检查
├── 权限验证
└── 依赖项检查 (git, python, node)

PHASE 3: SECURITY & PRIVACY SCAN      [本地]  ~15s  ★新增
├── 敏感文件扫描
├── 权限安全检查
├── 密码强度检查
├── 隐私泄露风险评估
└── 生成安全报告

PHASE 4: SKILLS AVAILABILITY CHECK    [本地]  ~10s  ★新增
├── 扫描本机所有skills
├── 验证SKILL.md完整性
├── 检查脚本可执行性
├── 测试依赖可用性
└── 标记损坏/缺失skills

PHASE 5: SKILLS UPDATE CHECK          [网络]  ~60s  ★新增
├── 联网搜索同类skills最新版本
├── 对比本机版本与在线版本
├── 检查官方仓库更新
├── 评估最佳实践差异
├── 自动拉取更新（如可用）
└── 生成更新建议报告

PHASE 6: BACKUP SYSTEM SYNC           [本地]  ~5s
├── 检查最新备份状态
├── 验证备份完整性
├── 如需要执行一键备份
├── 同步到GitHub私人仓库
└── Agent Bus通知

PHASE 7: MEMORY SYSTEM INITIALIZATION [本地]  ~5s
├── 加载Hot Memory (P0优先级)
├── 加载Warm Memory (P1/P2)
├── 恢复活跃Channel
├── 同步Memory Blocks
└── 验证记忆完整性

PHASE 8: GIT REPOSITORY SYNC          [本地]  ~10s
├── 检查Git仓库状态
├── 配置远程仓库
├── 拉取最新更改
├── 合并冲突处理
└── 创建同步标签

PHASE 9: HOOKS SYSTEM INITIALIZATION  [本地]  ~3s
├── 加载Hooks配置
├── 注册PreToolUse Hooks
├── 注册PostToolUse Hooks
├── 验证Hooks执行环境
└── 测试Hook触发

PHASE 10: AGENT ECOSYSTEM SYNC        [本地]  ~5s
├── 检查Agent Bus状态
├── 注册所有子Agents
├── 同步OpenClaw工作区
├── 加载AGENTS.md规则
└── 加载SOUL.md行为准则

PHASE 11: AGENT BUS SYNC              [本地]  ~5s   ★新增
├── 拉取其他Agents的最新信息
├── 读取Agent Bus通知队列
├── 同步跨Agent任务状态
├── 更新Agent间共享记忆
└── 广播本Agent就绪状态

PHASE 12: TASK STATUS REPORT          [本地]  ~10s  ★新增
├── 扫描本机正在运行的所有任务
├── 读取计划任务调度器(cron/scheduler)
├── 分析未来24小时内待执行的任务
├── 检查任务依赖关系
└── 生成任务状态报告

PHASE 13: READY STATE & REPORT        [本地]  ~3s
├── **UPTIME REPORT** - 显示自上次启动后的运行时长
├── 汇总所有阶段结果
├── 生成完整状态报告
├── 显示关键提醒和警告
├── 推荐下一步操作
└── 进入就绪状态
```

---

## 执行顺序设计原理

```
为什么这样排序？

1-2. 基础检查 (必须先确认系统健康)
       ↓
3.   安全隐私 (在联网前确保环境安全)
       ↓
4-5. Skills检查/更新 (在网络可用时尽早完成)
       ↓
6.   备份同步 (更新前确保有备份)
       ↓
7-9. 核心系统初始化 (加载记忆、Git、Hooks)
       ↓
10-11. Agent系统同步 (Agent间通信)
       ↓
12.  任务报告 (在系统就绪后报告任务)
       ↓
13.  最终就绪 (汇总输出)
```

---

## 详细功能说明

### PHASE 3: Security & Privacy Scan (安全隐私检查)

**执行内容**:
```powershell
# 调用 privacy-scanner skill
# 调用 security-check skill
# 生成 ~/.kimi/logs/security-scan-{timestamp}.json
```

**检查项目**:
- 敏感文件位置扫描
- 配置文件权限检查
- API密钥/密码泄露检测
- 未加密存储的凭据
- 过期的访问令牌

**输出**: 安全评分 (0-100) + 风险项目列表

---

### PHASE 4: Skills Availability Check (Skills可用性检查)

**执行内容**:
```powershell
# 扫描 ~/.kimi/skills/*/
# 检查每个skill的:
#   - SKILL.md 存在且有效
#   - 入口脚本可执行
#   - 依赖项已安装
#   - 配置文件完整
```

**输出**: 
- 可用Skills数量
- 损坏Skills列表
- 缺失依赖报告

---

### PHASE 5: Skills Update Check (Skills更新检查)

**执行内容**:
```powershell
# 对每个skill:
#   1. 解析SKILL.md中的元数据
#   2. 联网搜索官方仓库
#   3. 检查版本差异
#   4. 对比最佳实践
#   5. 生成更新建议
```

**更新策略**:
| 情况 | 处理方式 |
|------|----------|
| 官方有更新 | 自动拉取并备份旧版 |
| 本机为自定义 | 对比最佳实践，生成改进建议 |
| 依赖缺失 | 自动安装 |
| 损坏的skill | 尝试从备份恢复 |

**输出**: 更新报告 + 自动更新日志

---

### PHASE 11: Agent Bus Sync (Agent Bus信息拉取)

**执行内容**:
```powershell
# 1. 检查Agent Bus连接
# 2. 拉取未读通知
# 3. 同步其他Agents状态
# 4. 更新共享记忆
# 5. 广播本Agent就绪
```

**消息类型处理**:
- `BACKUP_COMPLETE` → 更新备份记录
- `CONFIG_UPDATE` → 提示重新加载配置
- `AGENT_WAKE` → 记录Agent启动
- `TASK_COMPLETE` → 更新任务状态

---

### PHASE 12: Task Status Report (任务状态报告)

**执行内容**:
```powershell
# 1. 扫描运行中任务
#    - Python进程
#    - PowerShell作业
#    - Node.js服务
#    - 计划任务
#
# 2. 读取任务调度器
#    - Windows Task Scheduler
#    - Cron jobs (WSL)
#    - 自定义调度器
#
# 3. 预测24小时内任务
#    - 基于历史模式
#    - 基于已调度任务
#    - 基于周期性任务
```

**输出示例**:
```
正在运行的任务 (3):
  [PID 1234] smart-backup-v3.ps1    运行中 12分钟
  [PID 5678] agent_bus.py          运行中 2小时
  [PID 9012] memory-sync.js        运行中 5分钟

未来24小时待执行任务 (5):
  14:00  自动备份 (每日)
  18:00  内存清理 (每日)
  明天 09:00  Skills更新检查 (每周)
  明天 12:00  安全扫描 (每周)
  明天 15:30  会议提醒 (一次性)
```

---

## 全局命令配置

### Windows PowerShell 配置

添加到 `$PROFILE`:

```powershell
# Wake Up Master 全局命令
function wake {
    param(
        [switch]$quick,
        [switch]$update,
        [switch]$security,
        [switch]$tasks
    )
    
    $script = "$env:USERPROFILE\.kimi\skills\wake-up-master\scripts\execute.ps1"
    
    if ($quick) {
        & "$env:USERPROFILE\.kimi\skills\wake-up-master\scripts\wake-up-simple.ps1"
    } elseif ($update) {
        & $script -SkipPhase @("Health","Security") -Focus "SkillsUpdate"
    } elseif ($security) {
        & $script -SkipPhase @("SkillsUpdate","TaskReport") -Focus "Security"
    } elseif ($tasks) {
        & $script -SkipPhase @("SkillsUpdate","Security") -Focus "Tasks"
    } else {
        & $script
    }
}

Set-Alias -Name "wake up" -Value wake
```

### 使用示例

```bash
wake up              # 完整13阶段唤醒
wake up --quick      # 快速模式（5阶段）
wake up --update     # 专注Skills更新检查
wake up --security   # 专注安全扫描
wake up --tasks      # 专注任务报告
```

---

## 配置选项

### 执行模式

| 模式 | 命令 | 说明 |
|------|------|------|
| **Normal** | `wake up` | 完整13阶段执行 |
| **Quick** | `wake up --quick` | 5阶段快速模式 |
| **Update** | `wake up --update` | 专注Skills更新 |
| **Security** | `wake up --security` | 专注安全检查 |
| **Tasks** | `wake up --tasks` | 专注任务报告 |
| **Repair** | `wake up --repair` | 修复模式 |

### 跳过选项

```bash
--skip-health          # 跳过健康检查
--skip-security        # 跳过安全扫描
--skip-skills-check    # 跳过Skills检查
--skip-skills-update   # 跳过Skills更新
--skip-backup          # 跳过备份同步
--skip-git             # 跳过Git同步
--skip-agent-bus       # 跳过Agent Bus
--skip-task-report     # 跳过任务报告
```

---

## 故障恢复

### 自动恢复机制

| 问题 | 自动处理 |
|------|----------|
| Skills损坏 | 从备份恢复 |
| 依赖缺失 | 自动安装 |
| Agent Bus断开 | 重连并同步 |
| 安全检查失败 | 生成修复建议 |
| 网络不可用 | 跳过联网功能 |

---

## 日志记录

```
~/.kimi/logs/wake-up-master/
├── wake-up-20260219-121234.log          # 主执行日志
├── security-scan-20260219-121234.json   # 安全扫描结果
├── skills-check-20260219-121234.json    # Skills检查结果
├── skills-update-20260219-121234.json   # 更新检查结果
├── agent-bus-20260219-121234.json       # Agent同步记录
└── task-report-20260219-121234.json     # 任务状态报告
```

---

## 版本信息

- **Version**: 2.0.0
- **Author**: KbotGenesis
- **Type**: Official Native Master Skill
- **Integration**: 全系统整合
- **Phases**: 13
- **Estimated Time**: 3-5 minutes (完整模式)

---

## Uptime Report (运行时长报告)

每次执行 `wake up` 后，系统会记录启动时间。下次执行时会显示自上次启动以来的运行时长：

```
UPTIME REPORT:
  System ran for: 2 days 5 hours 30 minutes
  Since: 2026-02-17T09:00:00.0000000+08:00
```

**存储位置**: `~/.kimi/memory/hot/last-wake-up.json`

**显示格式**:
- 天数 (days) - 如果大于0
- 小时数 (hours) - 如果大于0  
- 分钟数 (minutes) - 如果大于0
- 秒数 (seconds) - 如果小于1分钟

---

## 新增功能总结

| 新增功能 | 阶段 | 耗时 | 网络需求 |
|----------|------|------|----------|
| 安全隐私扫描 | 3 | ~15s | 否 |
| Skills可用性检查 | 4 | ~10s | 否 |
| Skills更新检查 | 5 | ~60s | **是** |
| Agent Bus同步 | 11 | ~5s | 可选 |
| 任务状态报告 | 12 | ~10s | 否 |
| Uptime运行时长报告 | 13 | ~0s | 否 |
| 全局命令支持 | - | - | - |

---

# 多维度分析报告与改进路线图

## 分析报告

本Skill已通过**第一性原理**、**系统思维**、**贝叶斯决策**、**博弈论**、**精益思想**五个维度进行深度分析。

详细分析报告见: `analysis-reports/wake-up-master-multi-lens-analysis.md`

---

## 核心发现

### 第一性原理分析
- **本质**: 唤醒的本质是系统状态的确认与同步
- **关键假设**: 串行执行是最优的、所有阶段对所有用户都有价值
- **改进方向**: 并行化优化、智能分层、场景化定制

### 系统思维分析
- **反馈回路**: 存在启动延迟恶性循环风险，需要负反馈调节
- **子系统划分**: A、B、C子系统必须串行；D子系统可以异步化
- **改进方向**: 子系统D异步化、实施断路器模式

### 贝叶斯决策分析
- **场景识别**: 可建立智能场景识别，动态调整检查深度
- **证据更新**: 基于距上次时间、Git状态、网络状态动态调整
- **改进方向**: 快速模式(<1小时)、标准模式(1-8小时)、完整模式(>8小时)

### 博弈论分析
- **多主体博弈**: 用户(快速)vs系统(稳定)vs安全(彻底)
- **纳什均衡**: (快速模式, 基础检查) 是双方效用最大化
- **改进方向**: 设计激励相容机制，平衡各方需求

### 精益思想分析
- **严重浪费**: 等待浪费(串行执行)最严重，可减少67%时间
- **关键路径**: Phase 3-5和Phase 10-13可并行化
- **改进方向**: 并行化优化至60秒、智能缓存、后台预热

---

## 改进路线图

### 立即实施 (1-2周)

1. **并行化Phase 3-5** [P0]
   - Privacy Scan, Skills Check, Update Check可同时执行
   - 预计节省: 30-40秒
   - 实现方式: PowerShell并行作业或异步脚本

2. **并行化Phase 10-13** [P0]
   - Agent Ecosystem, Agent Bus, Task Report可同时执行
   - 预计节省: 15-20秒
   - Phase 13汇总等待并行结果

3. **智能模式推荐** [P1]
   - 基于距上次唤醒时间自动推荐模式
   - <1小时: 建议快速模式(Phases 1,2,7,13)
   - 1-8小时: 建议标准模式(核心路径)
   - >8小时: 建议完整模式(所有13阶段)

### 短期改进 (1-2个月)

4. **增量检查机制** [P0]
   - Skills仅检查变更项（基于上次时间戳）
   - 安全扫描复用近期结果（如上次<24小时则跳过）
   - 预计节省: 40-50%检查时间

5. **后台预热** [P1]
   - 闲置时预执行非关键检查(Phase 4,5,12)
   - 唤醒时直接使用缓存结果
   - 预计节省: 20-30秒

6. **自适应流程** [P1]
   - 根据历史成功率动态调整检查深度
   - 高可靠环境(成功率>95%)减少检查项
   - 低可靠环境增加检查项

7. **智能故障恢复** [P2]
   - 非关键阶段失败不阻断整体
   - 自动诊断并修复常见问题
   - 目标: 自恢复率>80%

### 中期愿景 (3-6个月)

8. **预测性唤醒** [P2]
   - 基于使用模式预测唤醒需求
   - 提前开始准备工作
   - 目标: 用户感知唤醒时间<10秒

9. **个性化配置** [P2]
   - 用户可自定义阶段偏好
   - 场景化配置模板(开发/安全/生产)
   - 学习用户习惯自动优化

10. **系统健康仪表板** [P2]
    - 实时显示各组件健康度
    - 历史趋势分析
    - 预测性告警

---

## 更新后的架构愿景 (v3.0)

```
Wake Up Master v3.0
├── 触发层
│   ├── 用户手动触发
│   ├── 自动触发（开机/定时）
│   └── 智能触发（预测性）
├── 决策层
│   ├── 场景识别器
│   │   ├── 开发场景 → 轻量模式
│   │   ├── 生产场景 → 完整模式
│   │   └── 安全场景 → 深度模式
│   └── 深度计算器
│       ├── 基于距上次时间
│       ├── 基于系统变更
│       └── 基于网络状态
├── 执行层（并行化）
│   ├── 核心路径（串行）
│   │   ├── 系统健康检查 (Phase 1-2) ~8s
│   │   └── 环境验证
│   ├── 网络路径（并行）
│   │   ├── 安全检查 (Phase 3)
│   │   ├── Skills检查 (Phase 4)
│   │   └── 更新检查 (Phase 5) ~60s
│   ├── 同步路径（串行）
│   │   ├── 备份同步 (Phase 6)
│   │   ├── 记忆加载 (Phase 7)
│   │   └── Git同步 (Phase 8) ~25s
│   └── 生态路径（并行）
│       ├── Agent生态 (Phase 10)
│       ├── Agent Bus (Phase 11)
│       └── 任务报告 (Phase 12) ~20s
├── 优化层
│   ├── 智能缓存
│   ├── 增量检查
│   └── 后台预热
└── 反馈层
    ├── 性能监控
    ├── 用户反馈
    └── 持续优化

优化后总时间: ~60s (减少67%)
```

---

## 度量指标

| 指标 | 当前 | 目标 | 测量方法 |
|------|------|------|----------|
| 完整模式时间 | 3-5分钟 | <2分钟 | 日志记录 |
| 快速模式时间 | - | <30秒 | 日志记录 |
| 成功率 | >95% | >99% | 成功/总次数 |
| 用户满意度 | - | >4.5/5 | 定期调研 |
| 缓存命中率 | - | >60% | 缓存统计 |
| 自动恢复率 | - | >80% | 恢复日志 |

---

## 与其他Skill的协同

```
Wake Up Master ←→ One-Click Backup
    ↓
备份系统同步

Wake Up Master ←→ Privacy Scanner/Security Check
    ↓
安全隐私扫描

Wake Up Master ←→ Agent Bus
    ↓
多Agent生态同步

Wake Up Master ←→ Memory System
    ↓
记忆系统初始化

Wake Up Master ←→ Git Automation
    ↓
代码仓库同步
```

---

## 最佳实践

### 唤醒模式选择指南

```
快速模式 (--quick):
├── 适用: 开发迭代中频繁切换
├── 场景: 距上次<1小时，同一项目
└── 阶段: 1,2,7,13

标准模式 (默认):
├── 适用: 正常工作开始
├── 场景: 距上次1-8小时
└── 阶段: 1,2,4,6,7,8,10,13

完整模式 (--full):
├── 适用: 每日首次启动
├── 场景: 距上次>8小时或系统异常
└── 阶段: 所有13阶段

专注模式 (--update/--security/--tasks):
├── 适用: 特定需求
├── 场景: 仅需执行特定检查
└── 阶段: 相关子集
```

### 故障处理流程

```
Level 1: 单阶段失败
├── 非关键阶段: 记录日志，继续执行
└── 关键阶段: 尝试自动恢复，失败则告警

Level 2: 多阶段失败
├── 分析失败模式
├── 建议修复方案
└── 提供一键修复选项

Level 3: 系统级故障
├── 进入修复模式
├── 恢复到最后已知良好状态
└── 通知用户手动介入
```

---

*多维度分析报告生成时间: 2026-02-19*  
*方法论: 第一性原理 + 系统思维 + 贝叶斯决策 + 博弈论 + 精益思想*
