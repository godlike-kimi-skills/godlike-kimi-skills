# Memory Isolator

**工作记忆隔离保障** - Official Native Skill for Kimi CLI

确保不同项目、任务、会话之间的记忆完全隔离，防止上下文污染。借鉴Claude MCP Memory Keeper的Channel系统和Letta的Agent隔离机制，结合Kubernetes命名空间隔离和Docker容器安全模型。

---

## 核心概念

### 隔离级别

```
┌─────────────────────────────────────────────────────────┐
│                    GLOBAL (全局共享)                      │
│  - 用户偏好 (P0)                                         │
│  - 系统配置                                              │
│  - 跨项目共享的认证信息                                  │
│  访问控制: 只读 (大部分) / 受限写                        │
└─────────────────────────────────────────────────────────┘
                           ▲
┌─────────────────────────────────────────────────────────┐
│                 PROJECT (项目隔离)                        │
│  每个项目独立的记忆空间:                                    │
│  - KbotTrading/                                          │
│  - CryptoAnalysis/                                       │
│  - MarketResearch/                                       │
│  访问控制: Channel成员完全控制                           │
└─────────────────────────────────────────────────────────┘
                           ▲
┌─────────────────────────────────────────────────────────┐
│                SESSION (会话隔离)                         │
│  每次对话独立的临时上下文:                                  │
│  - working_memory/                                       │
│  - temp_files/                                           │
│  - context_cache/                                        │
│  访问控制: 会话期间有效，结束自动清理                    │
└─────────────────────────────────────────────────────────┘
```

### Channel系统 (MCP Memory Keeper风格)

```
Channel: KbotTrading
├── Metadata:
│   ├── id: "KbotTrading"
│   ├── created: "2026-02-19T10:00:00Z"
│   ├── owner: "user"
│   ├── encryption_key_id: "key-abc123"
│   └── integrity_hash: "sha256:def456"
├── Context: 加密交易自动化
├── Security Context:
│   ├── classification: "sensitive"
│   ├── allowed_operations: ["read", "write", "delete"]
│   └── data_residency: "local-only"
├── Blocks:
│   ├── wallet_config (encrypted)
│   ├── strategy_params (encrypted)
│   └── risk_limits (encrypted)
├── Sessions:
│   ├── session_20260219_001
│   ├── session_20260219_002
│   └── checkpoint_pre_update
├── Access Log:
│   ├── [2026-02-19 10:00] Created by user
│   ├── [2026-02-19 10:30] Read: wallet_config
│   └── [2026-02-19 11:00] Write: strategy_params
└── Status: active
```

---

## 使用方法

### 创建隔离Channel
```bash
# 创建新项目Channel
memory-isolator channel create --name "KbotTrading" --classification sensitive

# 创建带加密的Channel
memory-isolator channel create --name "CryptoAnalysis" --encrypt --key-rotation 30d

# 创建受限Channel（禁止全局变量访问）
memory-isolator channel create --name "HighSecurityProject" --strict-mode
```

### 切换Channel上下文
```bash
# 切换到指定Channel
memory-isolator channel switch --to "CryptoAnalysis"

# 查看当前Channel
memory-isolator channel current

# 列出所有Channel
memory-isolator channel list --show-security-info
```

### 创建检查点
```bash
# 创建检查点
memory-isolator checkpoint create --name "before_major_update" --description "重大更新前"

# 创建加密检查点
memory-isolator checkpoint create --name "pre_release" --encrypt --password-protected

# 列出检查点
memory-isolator checkpoint list --channel "KbotTrading"
```

### 恢复检查点
```bash
# 从检查点恢复
memory-isolator checkpoint restore --id "checkpoint_pre_update"

# 验证后恢复
memory-isolator checkpoint restore --id "checkpoint_v1" --verify-integrity

# 选择性恢复（仅恢复特定blocks）
memory-isolator checkpoint restore --id "checkpoint_v1" --blocks "wallet_config"
```

### 查看隔离状态
```bash
# 显示当前隔离状态和活跃Channel
memory-isolator status --verbose

# 查看污染检测报告
memory-isolator report contamination --since "24h"

# 安全审计报告
memory-isolator audit --channel "KbotTrading"
```

### 清理临时记忆
```bash
# 清理当前会话的临时数据
memory-isolator session cleanup --confirm

# 清理所有过期会话
memory-isolator session cleanup --expired-only

# 安全擦除（符合DoD标准）
memory-isolator session cleanup --secure-wipe
```

---

## 隔离机制

### 1. 命名空间隔离

```
memory://{channel}/{namespace}/{block}

示例:
memory://KbotTrading/project/wallet_config
memory://KbotTrading/session/temp_data
memory://KbotTrading/checkpoint/pre_update
memory://global/system/preferences

访问控制规则:
- project/* : Channel内完全访问
- session/* : 仅创建会话可读写
- checkpoint/* : 只读，恢复时临时写
- global/* : 只读，严格模式禁止访问
```

### 2. 上下文类型

| 类型 | 说明 | 生命周期 | 可跨Channel | 加密 |
|------|------|----------|-------------|------|
| `project` | 项目级记忆 | Channel存在期间 | 否 | 可选 |
| `session` | 会话级记忆 | 会话期间 | 否 | 强制 |
| `checkpoint` | 检查点快照 | 永久直到删除 | 否 | 强制 |
| `temp` | 临时数据 | 单次对话 | 否 | 否 |
| `global` | 全局共享 | 永久 | 是 | 否 |

### 3. 污染检测

自动检测以下情况并告警：
- 跨Channel引用未声明的全局变量
- 会话数据泄露到其他Channel
- 临时文件未清理
- 敏感数据意外写入非加密存储
- 未授权的全局变量修改尝试

**污染检测规则引擎**:
```yaml
rules:
  - name: "cross_channel_leak"
    pattern: "channel_a.*channel_b"
    severity: "critical"
    action: "block_and_alert"
    
  - name: "global_variable_misuse"
    pattern: "write_to_global.*sensitive"
    severity: "high"
    action: "require_approval"
    
  - name: "temp_cleanup_failure"
    pattern: "session_end.*temp_exists"
    severity: "medium"
    action: "auto_cleanup_and_log"
```

---

## 目录结构

```
.kimi/isolator/
├── channels/                    # Channel配置
│   ├── KbotTrading/
│   │   ├── meta.json           # Channel元数据
│   │   ├── manifest.json       # 完整性清单
│   │   ├── blocks/             # Memory Blocks
│   │   │   ├── wallet_config.json.enc
│   │   │   ├── strategy.json.enc
│   │   │   └── .integrity      # 哈希校验文件
│   │   ├── sessions/           # 会话历史
│   │   │   ├── 20260219_001/
│   │   │   │   ├── temp_data/
│   │   │   │   └── context.json
│   │   │   └── 20260219_002/
│   │   ├── checkpoints/        # 检查点
│   │   │   ├── checkpoint_pre_update.json.enc
│   │   │   └── checkpoint_v1_0.json.enc
│   │   └── audit.log           # 访问审计日志
│   └── CryptoAnalysis/
│       └── ...
├── global/                      # 全局共享
│   ├── system_config.json
│   └── user_preferences.json
├── active.json                  # 当前活跃Channel
├── registry.json                # Channel注册表
├── encryption/                  # 密钥管理
│   ├── keys/                    # 加密密钥
│   └── rotation.log             # 密钥轮换日志
└── isolation.log                # 隔离操作日志
```

---

## 检查点系统

### 完整状态快照

```json
{
  "checkpoint_id": "KbotTrading-pre-update-20260219103000",
  "channel": "KbotTrading",
  "timestamp": "2026-02-19T10:30:00+08:00",
  "integrity": {
    "algorithm": "sha256",
    "hash": "a1b2c3d4e5f6...",
    "signature": "sig-xyz789"
  },
  "encryption": {
    "algorithm": "AES-256-GCM",
    "key_id": "key-20260219-001"
  },
  "blocks_snapshot": {
    "wallet_config": { 
      "hash": "abc123", 
      "content_ref": "enc://blocks/wallet_config",
      "size": 2048,
      "modified": "2026-02-19T10:25:00Z"
    },
    "strategy_params": { 
      "hash": "def456", 
      "content_ref": "enc://blocks/strategy_params",
      "size": 1024,
      "modified": "2026-02-19T10:20:00Z"
    }
  },
  "context_summary": "更新前的钱包配置和策略参数",
  "session_context": {
    "last_task": "配置Solana钱包",
    "pending_actions": ["验证余额"],
    "variables": {
      "current_network": "mainnet"
    }
  },
  "access_control": {
    "created_by": "user",
    "allowed_to_restore": ["user", "admin"],
    "expires_at": "2026-03-19T10:30:00Z"
  }
}
```

### 检查点操作

```python
# 创建检查点
# 1. 计算所有blocks的哈希
# 2. 加密敏感blocks
# 3. 生成完整性签名
# 4. 写入加密存储
# 5. 更新审计日志
create_checkpoint(channel="KbotTrading", name="pre_update")

# 列出检查点
# - 验证完整性签名
# - 显示恢复可用性
list_checkpoints(channel="KbotTrading")

# 恢复到检查点
# 1. 验证完整性
# 2. 解密blocks
# 3. 验证哈希匹配
# 4. 原子性替换当前状态
# 5. 记录恢复操作
restore_checkpoint(checkpoint_id="KbotTrading-pre-update-20260219103000")

# 比较差异
# - 对比两个检查点的所有blocks
# - 显示新增、修改、删除的项目
diff_checkpoints(cp1="checkpoint_v1", cp2="checkpoint_v2")
```

---

## 变更追踪 (Diff Tracking)

### 自动记录变更

```
[2026-02-19 10:30:15] KbotTrading/wallet_config
  MODIFIED: solana_address
    FROM: 5VnAZ...CtW
    TO:   5VnAZ...CtW (更新标签)
  BY: user
  SESSION: 20260219_001
  CHECKSUM: sha256:abc123 → sha256:def456

[2026-02-19 10:35:22] KbotTrading/strategy_params
  ADDED: risk_limit_usd = 1000
  BY: user
  SESSION: 20260219_002
  
[2026-02-19 10:45:00] ⚠️  安全警告
  EVENT: 尝试引用未授权的Global变量
  CHANNEL: KbotTrading
  VARIABLE: api_key
  ACTION: BLOCKED
  BY: user
```

### 时间线视图

```
KbotTrading Channel Timeline
─────────────────────────────────────────────────
10:00  Channel created
10:05  Block added: wallet_config
10:10  Block added: strategy_params
10:30  Checkpoint created: before_update
10:35  Modified: strategy_params (风险限制)
10:40  Modified: wallet_config (添加Base钱包)
10:45  ⚠️  警告: 尝试引用未授权的Global变量 (已阻止)
10:50  Checkpoint created: after_wallet_setup
11:00  Session 20260219_001 ended, temp cleaned
─────────────────────────────────────────────────
```

---

## 安全架构

### 数据流安全

```
用户输入 → 污染检测 → 上下文路由 → 加密存储 → 完整性验证
    ↓           ↓            ↓            ↓             ↓
  输入验证   规则引擎   命名空间隔离  AES-256-GCM   SHA-256+HMAC
```

### 访问控制矩阵

| 操作 | 会话 | Channel成员 | Channel所有者 | 系统管理员 |
|------|------|-------------|---------------|------------|
| 读取Project | - | ✓ | ✓ | ✓ |
| 写入Project | - | ✓ | ✓ | ✓ |
| 读取Session | 自己的 | ✗ | ✓ | ✓ |
| 写入Session | 自己的 | ✗ | ✓ | ✓ |
| 创建Checkpoint | - | ✓ | ✓ | ✓ |
| 恢复Checkpoint | - | ✓ | ✓ | ✓ |
| 删除Channel | - | ✗ | ✓ | ✓ |
| 访问Global | - | 只读 | 只读 | 读写 |

---

## 深度安全分析

### 1. Threat Modeling (威胁建模)

Memory Isolator面临独特的隔离绕过威胁，需采用专门的威胁建模方法：

**侧信道攻击 (Side Channel)**：攻击者可能通过时间分析、缓存状态、资源使用模式推断其他Channel的数据。例如，通过观察加密操作时间推断密钥长度，或通过内存使用模式推断数据类型。建议实施常数时间加密操作，防止时间侧信道。内存访问随机化，避免缓存侧信道。资源使用规范化，固定周期执行清理操作。

**隔离逃逸 (Isolation Escape)**：恶意Channel可能尝试突破隔离边界访问其他Channel数据。可能通过符号链接遍历、路径注入、或利用文件系统竞争条件。建议实施严格的chroot隔离，每个Channel在独立文件系统命名空间。路径规范化，解析所有路径前进行安全检查。文件描述符隔离，防止通过继承的FD访问其他Channel。

**污染传播 (Contamination Spread)**：全局变量被恶意修改后可能影响所有Channel。会话数据未正确清理可能导致后续会话信息泄露。建议实施不可变全局变量，关键配置只读挂载。会话严格隔离，每个会话独立的内存空间。强制清理验证，会话结束必须验证临时数据已清除。

**检查点篡改 (Checkpoint Tampering)**：攻击者可能修改检查点数据，在恢复时植入恶意配置。检查点元数据被修改可能导致恢复到错误状态。建议实施检查点签名，每个检查点使用HMAC-SHA256签名。恢复前完整性验证，拒绝未通过验证的检查点。只读检查点存储，创建后不可修改。

**元数据泄露 (Metadata Leakage)**：即使数据加密，Channel名称、block数量、访问时间等元数据可能泄露敏感信息。建议实施元数据加密，Channel目录结构也进行加密。访问时间混淆，添加随机延迟掩盖真实访问模式。填充技术，固定Channel存储大小防止大小推断。

### 2. Defense in Depth (纵深防御)

内存隔离需要多层防御确保隔离边界不被突破：

**命名空间层防御**：每个Channel在独立的文件系统命名空间，使用chroot或容器技术隔离。进程命名空间隔离，防止Channel间进程间通信。网络命名空间隔离，Channel间网络流量受控。用户命名空间隔离，每个Channel使用独立的UID/GID映射。

**存储层防御**：Channel数据加密存储，即使物理介质被盗也无法解密。使用文件系统级加密(fscrypt)或卷加密(dm-crypt)。密钥派生使用Argon2id，抵抗暴力破解。定期密钥轮换，减少密钥泄露影响。

**内存层防御**：敏感数据仅在加密内存区域处理，使用mlock防止交换到磁盘。内存清零，数据使用后立即覆盖。ASLR和DEP启用，防止内存攻击。安全的内存分配器，防止堆喷和Use-After-Free。

**访问层防御**：细粒度访问控制，基于Channel成员身份授权。审计日志记录所有访问操作，支持事后追溯。异常访问检测，识别偏离基线的访问模式。会话超时机制，闲置会话自动锁定。

**传输层防御**：Channel间数据交换通过安全通道，禁止直接文件访问。序列化数据签名，防止传输中被篡改。传输加密，即使本地传输也使用TLS。传输完整性校验，检测中间人攻击。

### 3. Zero Trust (零信任)

零信任架构在内存隔离中的关键应用：

**永不信任Channel边界**：假设Channel隔离可能被突破，实施深度防御。假设全局变量可能被污染，使用时进行验证。假设检查点可能损坏，恢复前强制验证。持续监控隔离边界完整性，检测异常访问。

**持续验证Channel身份**：每次Channel访问都验证身份和授权，不依赖会话缓存。Channel切换时重新验证权限。定期重新认证长期活跃的Channel。设备状态检查，确保Channel在合规设备上访问。

**最小权限Channel访问**：Channel仅拥有完成任务所需的最小权限。临时权限提升，需要时动态申请，使用后释放。权限使用监控，检测异常权限使用。跨Channel访问需要显式授权。

**微分段Channel网络**：Channel间通信通过受控API网关，禁止直接访问。Channel部署在独立安全域，使用服务网格。东西向流量监控，检测异常Channel间通信。网络策略限制，仅允许必要的Channel间通信。

**假设Channel已失陷设计**：设计假设某个Channel已被攻陷。隔离失陷Channel的能力，防止影响扩散。突破检测机制，检测Channel异常行为。快速Channel重建能力，失陷后可快速恢复。

### 4. Risk Assessment (风险评估)

内存隔离风险评估需考虑上下文污染的严重性和隔离失效的连锁影响：

**关键风险识别**：
- 灾难性风险：隔离机制被完全绕过，敏感Channel数据泄露 (概率: 低，影响: 灾难性) - 风险等级: 严重
- 严重风险：全局变量污染导致所有Channel受影响 (概率: 低，影响: 严重) - 风险等级: 高
- 高风险：检查点篡改导致恶意配置恢复 (概率: 中，影响: 高) - 风险等级: 高
- 中风险：元数据泄露推断敏感信息 (概率: 中，影响: 中) - 风险等级: 中
- 中风险：会话数据未清理导致信息泄露 (概率: 中，影响: 中) - 风险等级: 中

**风险定量分析**：
- 上下文污染成本：错误决策可能导致重大业务损失
- 数据泄露成本：敏感Channel数据价值可能极高
- 隔离失效影响：单点失效可能影响所有Channel
- 恢复成本：Channel重建和数据恢复成本

**脆弱性评估**：
- 关键脆弱性：文件系统隔离依赖操作系统安全，可能存在逃逸漏洞
- 高危脆弱性：全局变量共享机制可能成为污染传播途径
- 中危脆弱性：检查点恢复可能引入过期的安全配置
- 低危脆弱性：Channel元数据可能泄露项目信息

**风险处置计划**：
| 风险 | 处置策略 | 控制措施 | 优先级 |
|------|----------|----------|--------|
| 隔离绕过 | 缓解 | 多层隔离+监控 | P0 |
| 全局污染 | 缓解 | 不可变全局+验证 | P0 |
| 检查点篡改 | 缓解 | 签名+验证 | P1 |
| 元数据泄露 | 接受 | 元数据加密 | P2 |

**持续风险监控KRI**：
- Channel边界访问尝试次数
- 全局变量修改尝试次数
- 检查点完整性验证失败次数
- 跨Channel数据传输量异常
- 会话清理失败次数

### 5. Compliance Framework (合规框架)

内存隔离需满足数据隔离和多租户安全合规要求：

**数据隔离合规**：
- GDPR Article 32：实施适当技术措施确保数据安全，包括隔离
- SOC 2 Type II：CC6.1 - 逻辑和物理访问控制，多租户隔离
- ISO 27001 A.8.15：日志隔离，防止租户间日志泄露
- 等保2.0：三级系统要求应用和数据层面隔离

**多租户安全合规**：
- CSA STAR：云安全联盟多租户安全要求
- PCI DSS 2.4/2.6：持卡人数据环境保护和共享主机安全
- HIPAA 164.312(a)(1)：访问控制，确保数据仅被授权访问

**隐私保护合规**：
- GDPR Article 25：设计和默认隐私保护，数据隔离是核心措施
- CCPA：消费者数据隔离保护
- 中国个人信息保护法：个人信息与系统数据隔离存储

**合规控制实现**：
- 强制Channel隔离，禁止跨Channel数据访问
- 数据分类标记，敏感数据必须存储于加密Channel
- 访问审计日志，记录所有跨边界访问尝试
- 定期隔离有效性验证，渗透测试验证隔离边界

**审计与证明**：
- Channel隔离架构文档化
- 隔离有效性测试报告
- 跨Channel访问审计日志
- 隔离违规事件处理记录

---

## 配置文件

```json
{
  "memory_isolator": {
    "version": "1.1.0",
    "default_channel": "default",
    "security_policy": {
      "encryption_required": true,
      "encryption_algorithm": "AES-256-GCM",
      "key_rotation_days": 30,
      "integrity_verification": "sha256+hmac",
      "strict_mode_default": false,
      "auto_cleanup_temp": true,
      "secure_wipe": true
    },
    "isolation_policy": {
      "strict_mode": true,
      "namespace_isolation": "filesystem+process",
      "global_access": "read-only",
      "cross_channel_access": "forbidden"
    },
    "limits": {
      "max_sessions_per_channel": 50,
      "max_checkpoints_per_channel": 20,
      "max_channel_storage_mb": 1024,
      "max_block_size_mb": 100
    },
    "audit": {
      "log_all_access": true,
      "log_retention_days": 90,
      "alert_on_violation": true
    },
    "channels": {
      "KbotTrading": {
        "created": "2026-02-19",
        "description": "加密交易自动化项目",
        "classification": "sensitive",
        "blocks": ["wallet_config", "strategy_params", "risk_limits"],
        "encryption": true,
        "active": true,
        "allowed_globals": []
      }
    },
    "global_blocks": [
      {
        "name": "user_preferences",
        "access": "read-only",
        "encryption": false
      },
      {
        "name": "system_config",
        "access": "read-only",
        "encryption": false
      }
    ]
  }
}
```

---

## 最佳实践

1. **一Channel一项目** - 每个独立项目使用独立Channel
2. **关键操作前检查点** - 重大变更前创建检查点
3. **及时清理临时数据** - 会话结束清理temp命名空间
4. **避免Global滥用** - 谨慎使用全局共享数据
5. **启用加密保护** - 敏感Channel必须启用加密
6. **定期轮换密钥** - 遵循配置的密钥轮换策略
7. **监控污染告警** - 及时处理隔离违规警告

---

## 相关技能

- `memory-directory-manager` - 记忆目录架构管理
- `memory-backup-scheduler` - 工作记忆备份调度
- `task-status` - 任务状态追踪
- `pre-operation-backup` - 操作前备份集成

---

## 参考实现

- **MCP Memory Keeper** (mkreyman/mcp-memory-keeper) - Channel & Checkpoint系统
- **Letta Agent Isolation** (letta-ai/letta) - Agent级隔离
- **Kubernetes Namespaces** - Kubernetes命名空间隔离
- **Docker Container Security** - Docker容器安全模型
- **gVisor** - 用户空间内核隔离

---

## 版本信息

- **Version**: 1.1.0 (安全架构增强版)
- **Author**: KbotGenesis (基于MCP Memory Keeper & Letta)
- **Type**: Official Native
- **Project**: KbotGenesis_Zero2Alpha_AutoVault
- **Compliance**: SOC 2, ISO 27001, GDPR, 等保2.0
- **Last Security Review**: 2026-02-19
