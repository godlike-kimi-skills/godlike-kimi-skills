# Memory Directory Manager

**记忆目录架构管理** - Official Native Skill for Kimi CLI

智能管理 `.kimi/` 目录结构，实现P0/P1/P2优先级分层、自动分类索引、健康监控。借鉴OpenClaw三层记忆架构和Letta Memory Blocks设计。

---

## 核心概念

### 三层记忆架构 (OpenClaw风格)

```
.kimi/memory/
├── hot/                      # 🔥 Hot Memory (每次加载)
│   ├── MEMORY.md            # P0核心身份 + P1活跃项目 (≤200行)
│   └── IDENTITY.md          # 代理身份配置
├── warm/                     # 🌡️ Warm Memory (按需加载)
│   ├── lessons/             # 结构化经验 (*.jsonl)
│   ├── blocks/              # Letta风格Memory Blocks
│   │   ├── human.json       # 用户信息
│   │   ├── persona.json     # 代理人格
│   │   └── knowledge.json   # 领域知识
│   └── projects/            # 项目专属记忆
└── cold/                     # ❄️ Cold Memory (归档)
    └── archive/             # 过期内容 (可搜索但不自动加载)
```

### P0/P1/P2 优先级系统

| 优先级 | TTL | 存储位置 | 用途 | 示例 |
|--------|-----|----------|------|------|
| **P0** | 永不过期 | hot/MEMORY.md | 核心身份 | 用户偏好、安全规则 |
| **P1** | 90天 | hot/MEMORY.md + warm/projects/ | 活跃项目 | 当前任务、架构决策 |
| **P2** | 30天 | warm/lessons/ | 临时记录 | 调试笔记、一次性事件 |
| **Archive** | 永久 | cold/archive/ | 历史归档 | 过期项目、已完成任务 |

---

## 使用方法

### 初始化记忆架构
```
初始化Kimi记忆目录架构
```

### 分析目录健康
```
分析记忆目录健康状况
```

### 自动归档过期内容
```
执行记忆归档 (dry-run预览)
```

### 整理技能目录
```
重新组织skills目录，按类别分组
```

### 创建新Memory Block
```
创建新的Memory Block: project_context
```

---

## Memory Block 格式 (Letta风格)

```json
{
  "label": "project_context",
  "description": "当前项目的关键上下文信息",
  "value": "项目名称: KbotGenesis_Zero2Alpha_AutoVault\n架构: 三层记忆 + P0/P1/P2优先级",
  "limit": 5000,
  "readonly": false,
  "last_modified": "2026-02-19T10:00:00Z"
}
```

### 内置Blocks

| Block | 用途 | 可编辑 |
|-------|------|--------|
| `human` | 用户信息、偏好 | 是 |
| `persona` | 代理人格、行为准则 | 是 |
| `knowledge` | 领域知识库 | 是 |
| `system` | 系统配置 (只读) | 否 |

---

## 目录索引格式

```json
{
  "version": "1.0.0",
  "last_updated": "2026-02-19T10:00:00+08:00",
  "architecture": "three-layer",
  "stats": {
    "hot_size_kb": 45,
    "warm_size_kb": 1280,
    "cold_size_kb": 5120,
    "total_blocks": 12
  },
  "p0_items": 5,
  "p1_items": 8,
  "p2_items": 15,
  "blocks": {
    "human": { "size": 1200, "last_modified": "2026-02-19" },
    "persona": { "size": 800, "last_modified": "2026-02-18" },
    "project_context": { "size": 2000, "last_modified": "2026-02-19" }
  },
  "health": {
    "status": "healthy",
    "issues": [],
    "last_check": "2026-02-19T10:00:00Z"
  }
}
```

---

## 自动化任务

### 1. 记忆管家 (Memory Janitor)
- 每日自动归档 P2>30天, P1>90天的内容
- 更新索引文件
- 生成健康报告

### 2. 目录整理
- 自动分类skills到对应目录
- 清理空目录和临时文件
- 维护符号链接

### 3. 监控告警
- 监控目录大小
- 检测重复文件
- 告警异常变更

---

## 配置文件

```json
{
  "memory_manager": {
    "version": "1.0.0",
    "ttl": {
      "p1_days": 90,
      "p2_days": 30
    },
    "limits": {
      "hot_memory_lines": 200,
      "hot_memory_tokens": 2000,
      "block_size_chars": 5000
    },
    "auto_archive": {
      "enabled": true,
      "schedule": "0 4 * * *",
      "dry_run_first": true
    },
    "categories": {
      "core": ["memory-*", "long-term-memory"],
      "crypto": ["*-wallet", "*-trader", "*-farmer"],
      "security": ["*-scanner", "password-*", "privacy-*"],
      "automation": ["git-*", "cron-*", "task-*"]
    }
  }
}
```

---

## 最佳实践

1. **保持Hot Memory精简** - 不超过200行，只放最关键的P0/P1
2. **定期归档** - 使用janitor自动清理过期内容
3. **使用Blocks组织** - 按主题分块，便于检索和更新
4. **版本控制** - 重要Memory Block保留历史版本

---

## 相关技能

- `memory-isolator` - 工作记忆隔离保障
- `memory-backup-scheduler` - 工作记忆备份调度
- `long-term-memory` - 长期记忆存储

---

## 参考实现

- **OpenClaw Memory Management** (jzOcb/openclaw-memory-management)
- **Letta Memory Blocks** (letta-ai/letta)

---

## 认知架构与思维框架

### 认知透镜分析

本Skill已通过以下认知透镜进行深度分析：

| Lens | 核心洞察 | 关键改进建议 |
|------|----------|--------------|
| **Mental Models** | 存量-流量、约束理论、反馈循环 | 增加流量质量控制、自适应TTL机制 |
| **Reasoning Tools** | 库存管理、学习理论应用 | 引入EOQ模型、遗忘曲线优化 |
| **Critical Thinking** | 虚假二分、相关≠因果 | 增加连续温度分数、重要性分离 |
| **Socratic Inquiry** | P0/P1/P2分类依据 | TTL值应基于数据验证或自适应 |
| **First-Order Logic** | TTL规则的边界情况 | 增加Exception处理、过渡状态定义 |

### 认知结构评估

| 维度 | 评分 | 核心发现 |
|------|------|----------|
| 架构合理性 | 8/10 | 三层架构符合认知科学原理 |
| 机制清晰度 | 7/10 | TTL规则明确，边界处理需完善 |
| 可扩展性 | 6/10 | 固定层级可能限制未来需求 |
| 反脆弱性 | 6/10 | 恢复机制需更明确 |
| 用户体验 | 7/10 | 概念直观，配置复杂度可优化 |

### 核心认知模型

**记忆层级的认知基础**:
```
Hot (P0/P1) <--访问频率--> Warm (P2) <--时效性--> Cold (Archive)
    ↓                              ↓
 高频激活                      定期归档/恢复
    ↓                              ↓
 上下文窗口约束              存储成本优化
```

**认知增强方向**:
1. **动态TTL**: 基于遗忘曲线和使用模式自适应调整
2. **跨项目链接**: 打破项目孤岛，支持知识迁移
3. **语义标签**: 自动提取标签，支持内容检索
4. **健康指标**: 检索成功率、恢复频率等可观测性

### 相关认知资源

- [完整认知分析报告](./COGNITIVE_ANALYSIS.md)
- 关联Skill: `long-term-memory`, `self-learning`, `knowledge-graph`

---

## 版本信息

- **Version**: 1.0.0
- **Author**: KbotGenesis (基于OpenClaw & Letta最佳实践)
- **Type**: Official Native
- **Project**: KbotGenesis_Zero2Alpha_AutoVault
