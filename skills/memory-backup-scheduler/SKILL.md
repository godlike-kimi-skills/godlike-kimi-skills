# Memory Backup Scheduler

**工作记忆备份调度** - Community Featured Skill for Kimi CLI

自动调度备份任务，支持增量备份、多目标存储、GitHub同步。借鉴Claude Code层叠CLAUDE.md系统和OpenClaw自动归档机制。

---

## 核心特性

### 备份策略矩阵

| 类型 | 频率 | 保留 | 存储 | 用途 |
|------|------|------|------|------|
| **实时** | 事件触发 | 最近10次 | 本地 | 关键操作前自动备份 |
| **增量** | 每小时 | 48小时 | 本地+云端 | 快速恢复 |
| **差异** | 每日 | 7天 | 本地+GitHub | 日常保护 |
| **完整** | 每周 | 4周 | GitHub+冷存储 | 灾难恢复 |
| **归档** | 每月 | 永久 | 冷存储 | 历史留存 |

### 三层备份架构

```
┌─────────────────────────────────────────┐
│  TIER 1: Hot Backup (实时)               │
│  ~/.kimi/backup/hot/                    │
│  - 最近10次操作                          │
│  - 内存级访问速度                        │
└─────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────┐
│  TIER 2: Warm Backup (增量/差异)          │
│  D:/kimi/Backups/incremental/           │
│  - 48小时内的变更                        │
│  - 快速恢复                              │
└─────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────┐
│  TIER 3: Cold Backup (完整/归档)          │
│  GitHub: wangjohnny9955/Kbot-backup     │
│  - 历史版本                              │
│  - 灾难恢复                              │
└─────────────────────────────────────────┘
```

---

## 使用方法

### 立即执行备份
```
立即执行完整备份到所有目标
```

### 配置自动调度
```
配置自动备份: 每天凌晨3点执行增量备份
```

### 创建检查点前备份
```
在修改配置文件前创建检查点备份
```

### 查看备份历史
```
显示最近7天的备份历史
```

### 恢复指定版本
```
从备份恢复: incremental-20260219-030000
```

### 验证备份完整性
```
验证所有备份的完整性
```

---

## 备份内容

### 优先级备份列表

```yaml
P0 (关键 - 每次必备份):
  - ~/.kimi/memory/hot/MEMORY.md
  - ~/.kimi/memory/hot/IDENTITY.md
  - ~/.kimi/isolator/active.json
  - ~/.kimi/config.toml

P1 (重要 - 增量备份):
  - ~/.kimi/skills/*/SKILL.md
  - ~/.kimi/memory/warm/blocks/*.json
  - ~/.kimi/memory/warm/projects/*/
  - ~/.kimi/isolator/channels/*/

P2 (可选 - 定期备份):
  - ~/.kimi/memory/warm/lessons/*.jsonl
  - ~/.kimi/memory/cold/archive/
  - ~/.kimi/logs/
```

---

## 调度配置

### Cron表达式支持

```json
{
  "schedules": [
    {
      "name": "hot_backup",
      "cron": "*/10 * * * *",
      "description": "每10分钟执行Hot备份",
      "type": "incremental",
      "targets": ["local"],
      "priority": "P0"
    },
    {
      "name": "daily_incremental",
      "cron": "0 3 * * *",
      "description": "每天凌晨3点增量备份",
      "type": "incremental",
      "targets": ["local", "github"],
      "priority": "P1"
    },
    {
      "name": "weekly_full",
      "cron": "0 4 * * 0",
      "description": "每周日凌晨4点完整备份",
      "type": "full",
      "targets": ["local", "github", "archive"],
      "priority": "P0+P1"
    }
  ]
}
```

### 事件触发备份

```json
{
  "event_triggers": [
    {
      "event": "session_end",
      "action": "backup_p0",
      "description": "会话结束时备份关键记忆"
    },
    {
      "event": "channel_switch",
      "action": "backup_channel_state",
      "description": "切换Channel前备份当前状态"
    },
    {
      "event": "memory_block_modified",
      "action": "backup_block",
      "delay_seconds": 60,
      "description": "Memory Block修改后60秒备份"
    }
  ]
}
```

---

## 多目标存储

### 本地存储

```
D:/kimi/Backups/
├── hot/                    # 实时备份
│   └── latest/ -> symlink
├── incremental/            # 增量备份
│   ├── 20260219-030000/
│   └── 20260219-040000/
├── full/                   # 完整备份
│   └── weekly-2026-W07/
└── archive/                # 归档备份
    └── 2026-02/
```

### GitHub同步

```json
{
  "github": {
    "repo": "wangjohnny9955/Kbot-backup",
    "branch": "main",
    "auto_push": true,
    "retry": {
      "max_attempts": 3,
      "delay_minutes": 10
    },
    "include": [
      "memory/**",
      "skills/**/SKILL.md",
      "isolator/**"
    ],
    "exclude": [
      "**/node_modules/**",
      "**/__pycache__/**",
      "**/temp/**"
    ]
  }
}
```

---

## 备份报告

### 实时状态

```json
{
  "backup_status": {
    "last_backup": "2026-02-19T10:30:00+08:00",
    "last_successful": "2026-02-19T10:30:00+08:00",
    "next_scheduled": "2026-02-19T11:00:00+08:00",
    "total_backups_today": 15,
    "storage_usage": {
      "local_mb": 1250,
      "github_commits": 48
    }
  },
  "health": {
    "status": "healthy",
    "last_verify": "2026-02-19T09:00:00Z",
    "integrity_check": "passed"
  }
}
```

### 每日摘要

```
📊 Backup Report - 2026-02-19
═══════════════════════════════════════
✅ 成功备份: 15次
⚠️  警告: 1次 (GitHub推送延迟)
❌ 失败: 0次

存储统计:
  本地: 1.25 GB (30天保留)
  GitHub: 48 commits
  归档: 5.2 GB (永久保留)

最近备份:
  10:30 增量备份 → 成功 (45KB)
  10:00 增量备份 → 成功 (12KB)
  09:30 增量备份 → 成功 (8KB)
```

---

## 恢复操作

### 恢复模式

```
1. 精确恢复 - 恢复到指定备份版本
2. 时间点恢复 - 恢复到指定时间点最近版本
3. 选择性恢复 - 仅恢复指定文件/目录
4. 合并恢复 - 合并多个备份版本
```

### 恢复命令

```
# 列出可用恢复点
list-restore-points --days 7

# 精确恢复
restore --backup-id incremental-20260219-030000

# 时间点恢复
restore --time "2026-02-19 10:00:00"

# 选择性恢复
restore --backup-id weekly-2026-W07 --include "skills/memory-*"
```

---

## 学习科学深度分析

### 🧠 间隔重复 (Spaced Repetition) 视角

Memory Backup Scheduler 是间隔重复原理在**数据持久化领域**的完美映射。系统的五层备份策略（实时、增量、差异、完整、归档）本质上是一个精心设计的间隔复习计划——只不过这里的"记忆"是AI的工作状态数据。

**间隔架构的科学性**：
- **实时备份（10分钟间隔）**：对应工作记忆的即时巩固，类似于学习中每读完一章就立即回顾关键概念。P0级关键数据的高频备份确保即使系统崩溃，最近的工作也不会丢失。
- **每日增量（24小时间隔）**：对应艾宾浩斯遗忘曲线的第一次复习节点。研究表明，24小时后的复习可以将记忆留存率从30%提升到80%。
- **每周完整（7天间隔）**：对应第二次复习节点，此时记忆开始从短期存储向长期存储转化。
- **每月归档（30天间隔）**：对应长期记忆的固化阶段，类似于月度知识复盘。

**改进建议**：引入基于"记忆重要性"的动态间隔算法。对于高频访问的P0数据采用更短的初始间隔（如5分钟），对于不常变动的P2数据则可以延长间隔。可参考SuperMemo-2算法，根据数据变化频率自适应调整备份间隔。

### 🎯 刻意练习 (Deliberate Practice) 视角

备份调度器本身虽然不直接涉及技能学习，但其设计理念与刻意练习的**渐进式难度提升**和**即时反馈**原则高度契合。

**渐进式备份复杂度**：
系统从简单的本地热备份（Hot）开始，逐步过渡到增量、差异、完整备份，最终到多目标云端同步。这种渐进式架构让管理员可以从简单配置开始，随着需求增长逐步引入更复杂的备份策略——这正是刻意练习中"在舒适区边缘训练"的体现。

**即时反馈循环**：
备份报告系统提供了丰富的反馈指标——成功次数、警告、失败、存储统计。这类似于运动员的实时数据监控，让管理员能够立即发现问题并调整策略。

**改进建议**：引入"备份技能训练模式"——为新用户设计一系列渐进式备份任务（从简单文件备份到复杂多目标同步），每个任务完成后给予反馈和评分。建立"备份策略最佳实践库"，让用户可以通过模仿学习掌握高级备份技巧。

### 🔄 迁移学习 (Transfer Learning) 视角

备份调度器展示了跨领域迁移的典范——它将数据库领域的**3-2-1备份法则**、版本控制的**Git同步机制**、以及分布式系统的**多副本策略**迁移到AI工作记忆管理场景。

**迁移的技术要素**：
- **3-2-1法则迁移**：3份备份、2种介质、1份异地——这个来自企业IT的黄金法则被完美适配到个人AI工作空间。
- **Git工作流迁移**：GitHub同步机制借鉴了Git的分布式版本控制思想，每次备份对应一次commit，支持历史回溯和分支管理。
- **冷热分层迁移**：源自云计算存储成本优化的冷热数据分层策略，被应用于本地备份架构设计。

**改进建议**：建立"备份模式知识库"，收录不同领域的备份最佳实践（如金融行业的实时复制、医疗行业的不可篡改存档），并提供迁移适配指南。开发"场景模板"功能，让用户可以一键应用特定领域的备份策略（如"开发者模板"、"内容创作者模板"）。

### 🎓 元认知 (Metacognition) 视角

备份调度器体现了极强的**元认知监控**能力——它不仅执行备份，还持续监控备份的健康状态、评估恢复可行性、预测存储需求。

**元认知监控机制**：
- **完整性检查**：定期验证备份数据的可读性和一致性，类似于学习者定期自我测试。
- **健康状态追踪**：实时监控备份成功率、存储空间、同步延迟，及时发现"学习异常"。
- **恢复演练**：通过选择性恢复功能，管理员可以验证备份是否真的可用——这是元认知中的"理解验证"。

**计划与监控分离**：
系统的调度配置（计划）与备份报告（监控）分离设计，体现了元认知理论中"计划-监控-评估"的循环结构。

**改进建议**：引入"备份健康度评分"，综合成功率、时效性、完整性等指标给出单一健康指数。开发"备份策略优化建议"功能，基于历史数据推荐更优的备份配置（如"检测到您的P1数据变化频率高，建议将增量备份间隔从1小时缩短至30分钟"）。

### 🌱 成长思维 (Growth Mindset) 视角

备份调度器的设计哲学深刻体现了成长思维——将"失败"重新定义为"学习机会"，将"数据丢失"视为"系统进化的催化剂"。

**拥抱失败的设计**：
系统的重试机制（GitHub推送最多3次尝试）和失败恢复策略（从备份自动恢复）传达了一个信息：失败是过程的一部分，关键在于如何从中恢复和学习。这对应成长思维中的"从挫折中学习"。

**持续改进的文化**：
备份策略不是一成不变的，系统支持动态调整调度频率、保留策略、存储目标。这体现了"能力可以通过努力发展"的成长思维核心信念。

**改进建议**：在备份报告中加入"改进建议"板块，不仅展示数据，还主动提出优化方案。设计"备份成熟度模型"，让用户看到自己的备份策略从"基础"到"企业级"的成长路径。引入"社区最佳实践分享"，让用户可以学习他人的备份策略并迁移到自己的场景。

---

## 配置文件

```json
{
  "memory_backup_scheduler": {
    "version": "1.1.0",
    "enabled": true,
    "backup_root": "D:/kimi/Backups",
    "retention": {
      "hot": { "count": 10 },
      "incremental": { "days": 7 },
      "full": { "weeks": 4 },
      "archive": { "months": 12 }
    },
    "compression": {
      "enabled": true,
      "level": 6,
      "exclude_patterns": ["*.jpg", "*.png", "*.mp4"]
    },
    "encryption": {
      "enabled": false,
      "method": "gpg"
    },
    "notifications": {
      "on_success": false,
      "on_failure": true,
      "channels": ["console", "log"]
    },
    "health_check": {
      "enabled": true,
      "interval_hours": 24,
      "verify_integrity": true
    },
    "learning_enhanced": {
      "adaptive_intervals": true,
      "spaced_repetition_algorithm": "supermemo2",
      "backup_skill_training": false,
      "pattern_migration_suggestions": true
    }
  }
}
```

---

## 最佳实践

1. **3-2-1备份法则** - 3份备份，2种介质，1份异地
2. **定期验证** - 每月验证备份可恢复性
3. **关键操作前检查点** - 重大变更前手动创建检查点
4. **监控存储空间** - 设置存储上限告警
5. **渐进式策略** - 从简单备份开始，逐步引入复杂策略
6. **失败即学习** - 分析备份失败原因，持续优化配置

---

## 相关技能

- `memory-directory-manager` - 记忆目录架构管理
- `memory-isolator` - 工作记忆隔离保障
- `git-automation` - Git自动备份集成
- `self-learning` - 自适应学习系统

---

## 参考实现

- **OpenClaw Memory Janitor** (jzOcb/openclaw-memory-management)
- **Claude Code CLAUDE.md** (级联配置系统)
- **SuperMemo-2 Algorithm** (间隔重复算法)
- **3-2-1 Backup Rule** (IT灾难恢复最佳实践)

---

## 版本信息

- **Version**: 1.1.0 (2026 学习科学增强版)
- **Author**: KbotGenesis (Community Featured)
- **Type**: Community Featured
- **Project**: KbotGenesis_Zero2Alpha_AutoVault
