# Wake Up 系统清单

## 1. 现有的 Wake Up 相关文件

### OpenClaw 引导系统
| 文件 | 路径 | 功能 |
|------|------|------|
| **BOOTSTRAP.md** | `~/.openclaw/workspace/BOOTSTRAP.md` | 首次启动引导 |
| **AGENTS.md** | `~/.openclaw/workspace/AGENTS.md` | Agent行为规范 |
| **SOUL.md** | `~/.openclaw/workspace/SOUL.md` | 核心行为准则 |
| **IDENTITY.md** | `~/.openclaw/workspace/IDENTITY.md` | 身份配置 |

### Kimi CLI 初始化
| 文件 | 路径 | 功能 |
|------|------|------|
| **init-wizard.py** | `~/.kimi/scripts/init-wizard.py` | 交互式配置向导 |
| **Kbot_Git_Init.ps1** | `~/.kimi/scripts/git-automation/` | Git仓库初始化 |

### Hooks 系统
| 文件 | 路径 | 功能 |
|------|------|------|
| **hooks.md** | `~/.kimi/rules/common/hooks.md` | Hooks使用指南 |
| SessionStart | 概念 | 会话开始时触发 |
| SessionEnd | 概念 | 会话结束时触发 |

## 2. 新创建的 Wake Up Skill

### 位置
```
~/.kimi/skills/wake-up/
├── SKILL.md                    # 技能文档
├── WAKE_UP_INVENTORY.md        # 本清单
└── scripts/
    ├── wake-up.ps1            # 完整功能版 (有编码问题)
    └── wake-up-simple.ps1     # 简化版 (工作正常)
```

### 功能
新创建的 wake-up skill 执行以下5步流程：

1. **System Health Check** - 系统健康检查
   - 磁盘空间
   - 内存使用
   - 网络连接

2. **Backup Verification** - 备份验证
   - 检查最新备份
   - 验证备份完整性
   - 显示备份统计

3. **Memory Loading** - 记忆加载
   - Hot Memory (P0)
   - Identity
   - Memory Blocks

4. **Agent Synchronization** - Agent同步
   - Agent Bus状态
   - 注册Agent数量
   - 消息队列状态

5. **Ready State** - 就绪状态
   - 显示系统状态
   - 列出可用命令
   - 欢迎消息

## 3. Wake Up 触发方式

### 用户说：
```
wake up
启动系统
wake up --quick
wake up --refresh
```

### 系统执行：
```powershell
# 使用新创建的skill
~/.kimi/skills/wake-up/scripts/wake-up-simple.ps1

# 或使用完整版（修复后）
~/.kimi/skills/wake-up/scripts/wake-up.ps1
```

## 4. 相关组件调用关系

```
用户说: "wake up"
    ↓
查找: wake-up skill
    ↓
执行: wake-up-simple.ps1
    ├── Step 1: 系统健康检查
    │   └── Get-WmiObject (Disk, Memory)
    │
    ├── Step 2: 备份验证
    │   └── 检查 D:\kimi\SmartBackups\
    │   └── 调用 one-click-backup (如需要)
    │
    ├── Step 3: 记忆加载检查
    │   └── 检查 ~/.kimi/memory/hot/
    │   └── 检查 ~/.kimi/memory/warm/blocks/
    │
    ├── Step 4: Agent同步检查
    │   └── 检查 ~/.kimi/agent-bus/
    │   └── 读取 subscribers.json
    │
    └── Step 5: 显示就绪状态
        └── 显示系统报告
        └── 列出可用命令
```

## 5. 对比：旧系统 vs 新系统

| 功能 | 旧系统 | 新 Wake Up Skill |
|------|--------|------------------|
| **触发方式** | 分散在多个文件 | 统一入口 |
| **引导流程** | BOOTSTRAP.md (手动) | 自动5步检查 |
| **系统检查** | 无 | 健康检查 |
| **备份检查** | 无 | 自动验证 |
| **记忆加载** | 手动 | 自动检查 |
| **Agent同步** | 无 | 自动检查 |
| **状态报告** | 无 | 完整报告 |

## 6. 使用建议

### 日常使用
```powershell
# 标准唤醒流程
~/.kimi/skills/wake-up/scripts/wake-up-simple.ps1

# 快速模式（跳过详细检查）
~/.kimi/skills/wake-up/scripts/wake-up-simple.ps1 -Mode quick
```

### 作为 Skill 调用
当用户说 "wake up" 时，应该：
1. 执行 `wake-up-simple.ps1`
2. 显示执行结果
3. 根据结果给出建议

### 集成到现有系统
- 可以替换 BOOTSTRAP.md 的手动流程
- 可以作为 HEARTBEAT.md 的任务
- 可以集成到 OpenClaw 的启动流程

## 7. 待修复问题

### 完整版脚本 (wake-up.ps1)
- 存在 PowerShell 特殊字符编码问题
- 需要替换中文标点符号和特殊Unicode字符
- 建议使用纯ASCII字符重写

### 简化版脚本 (wake-up-simple.ps1)
- ✅ 工作正常
- ✅ 无编码问题
- ⚠️ 功能相对简化

## 8. 推荐做法

**短期**：使用 `wake-up-simple.ps1`
**长期**：修复 `wake-up.ps1` 的编码问题，或使用 Python 重写

## 9. 版本信息

- **Version**: 1.0.0
- **Created**: 2026-02-19
- **Author**: KbotGenesis
- **Type**: Official Native Skill
