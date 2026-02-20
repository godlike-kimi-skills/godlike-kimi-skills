# Security Audit System

**生产级系统安全审计** - 借鉴 Lynis、OpenVAS、CIS Benchmarks

自动化系统安全评估、漏洞扫描、合规检查，提供可执行的安全加固建议。

---

## 核心特性

### 🔍 审计模块 (借鉴 Lynis)

| 模块 | 检查项 | 风险等级 |
|------|--------|----------|
| **系统信息** | 内核版本、发行版、架构 | 信息 |
| **启动与引导** | GRUB配置、Secure Boot、启动项 | 高 |
| **内核安全** | 内核参数、模块、Sysctl加固 | 高 |
| **内存管理** | ASLR、DEP/NX、交换加密 | 中 |
| **认证授权** | PAM配置、密码策略、sudoers | 高 |
| **用户账户** | UID 0、过期账户、空密码 | 高 |
| **权限管理** | SUID/SGID文件、世界可写 | 高 |
| **文件完整性** | 关键系统文件哈希校验 | 中 |
| **网络防护** | 防火墙、TCP包装、端口监听 | 高 |
| **SSH安全** | 配置加固、密钥认证、协议版本 | 高 |
| **恶意软件** | Rootkit检测、病毒扫描 | 高 |
| **日志审计** | rsyslog、auditd、日志权限 | 中 |

### 🛡️ 安全基准 (CIS Benchmarks)

```
CIS Level 1: 基础安全 - 不影响服务的最小加固
├── 最小化安装
├── 文件系统权限
├── 账户安全
└── 基本网络防护

CIS Level 2: 深度防御 - 全面的安全控制
├── 强制访问控制 (SELinux/AppArmor)
├── 审计日志
├── 入侵检测
└── 高级网络隔离
```

---

## 使用方法

### 快速审计
```bash
# 完整系统审计 (Level 1 + Level 2)
python ~/.kimi/skills/security-check/scripts/audit.py --level full

# 仅基础安全审计
python ~/.kimi/skills/security-check/scripts/audit.py --level 1

# 特定模块审计
python ~/.kimi/skills/security-check/scripts/audit.py --module ssh,auth,network
```

### 实时扫描
```bash
# 监听端口扫描
python ~/.kimi/skills/security-check/scripts/network.py --scan ports

# Rootkit检测
python ~/.kimi/skills/security-check/scripts/malware.py --scan rootkit

# SUID/SGID文件审计
python ~/.kimi/skills/security-check/scripts/filesystem.py --find-suid
```

### 合规检查
```bash
# CIS Level 1 合规
python ~/.kimi/skills/security-check/scripts/compliance.py --standard cis-1

# 生成合规报告
python ~/.kimi/skills/security-check/scripts/compliance.py --report html
```

---

## 审计报告

### 风险评级

| 等级 | 颜色 | CVSS范围 | 处理建议 |
|------|------|----------|----------|
| **严重** | 🔴 | 9.0-10.0 | 立即处理 |
| **高危** | 🟠 | 7.0-8.9 | 24小时内 |
| **中危** | 🟡 | 4.0-6.9 | 1周内 |
| **低危** | 🟢 | 0.1-3.9 | 计划处理 |
| **信息** | ⚪ | 0.0 | 参考 |

### 报告示例

```json
{
  "scan_id": "sec-20260219-001",
  "timestamp": "2026-02-19T10:30:00Z",
  "system": {
    "os": "Windows 11 Pro",
    "version": "23H2",
    "architecture": "x64"
  },
  "summary": {
    "total_checks": 150,
    "passed": 125,
    "warnings": 20,
    "critical": 5
  },
  "findings": [
    {
      "id": "AUTH-001",
      "title": "密码策略未配置复杂度要求",
      "severity": "high",
      "cvss": 7.5,
      "description": "系统未启用密码复杂度策略，允许弱密码",
      "remediation": "配置密码策略：最小长度14，复杂度要求启用",
      "reference": "CIS 1.1.1"
    }
  ],
  "hardening_index": 85  // 0-100 安全评分
}
```

---

## 技术实现

### 审计引擎架构

```
┌─────────────────────────────────────────┐
│           审计引擎 (Audit Engine)         │
├─────────────────────────────────────────┤
│  插件系统 → 动态加载审计模块              │
│  规则引擎 → CIS规则匹配                   │
│  评分系统 → CVSS v3.1计算                 │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│           审计模块 (Audit Modules)        │
├─────────────────────────────────────────┤
│  System → 系统信息收集                   │
│  Kernel → 内核安全检查                   │
│  Auth   → 认证授权审计                   │
│  Network→ 网络防护扫描                   │
│  Files  → 文件权限审计                   │
│  Malware→ 恶意软件检测                   │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│           报告生成器 (Reporter)           │
├─────────────────────────────────────────┤
│  JSON   → 机器可读                        │
│  HTML   → 可视化报告                      │
│  PDF    → 合规文档                        │
└─────────────────────────────────────────┘
```

### 关键检查实现

#### SSH加固检查 (CIS 5.2)
```python
checks = {
    'Protocol 2': 'required',           # 仅SSHv2
    'PermitRootLogin': 'no',           # 禁止root登录
    'PasswordAuthentication': 'no',    # 密钥认证
    'X11Forwarding': 'no',             # 禁用X11
    'MaxAuthTries': '4',               # 最大重试
    'ClientAliveInterval': '300',      # 心跳检测
    'LoginGraceTime': '60',            # 登录超时
    'Banner': '/etc/ssh/banner',       # 法律声明
}
```

#### 内核参数加固 (CIS 3.1)
```python
sysctl_rules = {
    'kernel.randomize_va_space': 2,     # ASLR
    'kernel.kptr_restrict': 2,          # 内核指针隐藏
    'kernel.dmesg_restrict': 1,         # dmesg限制
    'kernel.sysrq': 0,                  # 禁用SysRq
    'fs.suid_dumpable': 0,              # 禁用SUID core dump
    'net.ipv4.icmp_echo_ignore_broadcasts': 1,  # 忽略广播ping
    'net.ipv4.conf.all.rp_filter': 1,   # 反向路径过滤
}
```

---

## 深度安全分析

### 1. Threat Modeling (威胁建模)

Security Check Skill面临多维度攻击威胁，需采用STRIDE威胁建模框架进行系统性分析：

**欺骗威胁 (Spoofing)**：攻击者可能伪装成合法审计进程注入恶意检查规则，或伪造审计报告掩盖系统漏洞。审计脚本执行时需高权限，若被篡改可导致权限提升。建议实施代码签名验证，确保所有审计模块完整性，使用SHA-256哈希校验脚本文件。

**篡改威胁 (Tampering)**：审计结果存储文件可能被攻击者修改以隐藏入侵痕迹。CIS基准配置文件若被篡改，会导致合规检查失效。需实施审计日志的只读存储，使用WORM (Write Once Read Many) 技术保护关键审计数据，并建立审计链完整性验证机制。

**否认威胁 (Repudiation)**：缺乏不可抵赖的审计追踪机制，管理员可能否认执行过危险操作。建议集成数字签名和时间戳服务，所有审计操作记录到只追加日志，并定期将哈希值提交到区块链或外部时间戳服务器。

**信息泄露 (Information Disclosure)**：审计过程会收集系统敏感信息（用户列表、网络配置、漏洞详情），若报告文件权限配置不当，可被低权限用户读取。CVSS评分数据可能暴露系统脆弱点。需实施报告文件加密存储，分级访问控制，敏感数据脱敏处理。

**拒绝服务 (Denial of Service)**：审计扫描本身可能成为DoS攻击向量，高频系统调用影响生产环境性能。大规模网络扫描触发IDS/IPS警报。建议实施审计节流机制，设置资源使用上限，提供"审计模式"选项（快速/标准/深度）。

**权限提升 (Elevation of Privilege)**：SUID/SGID文件检测模块需要root权限执行，若存在漏洞可被利用。审计脚本解析配置文件时可能存在命令注入。需最小权限原则，使用 capabilities 替代完整root权限，严格的输入验证和沙箱执行环境。

### 2. Defense in Depth (纵深防御)

本Skill实施多层防御架构，确保单点失效不会导致整体安全控制崩溃：

**物理/网络层防御**：审计数据传输使用TLS 1.3加密通道，防止中间人攻击。网络扫描模块实施速率限制，避免被识别为恶意扫描源。关键审计报告存储于加密卷，防止物理介质被盗导致的数据泄露。

**主机层防御**：审计引擎运行在受限沙箱环境中，使用seccomp-bpf限制系统调用。实施地址空间布局随机化(ASLR)和数据执行保护(DEP)。关键审计模块使用只读文件系统挂载，防止运行时篡改。部署文件完整性监控(FIM)，检测审计工具本身的异常修改。

**应用层防御**：输入数据严格校验，使用白名单策略过滤配置参数。实施代码签名和完整性验证，所有审计脚本必须通过GPG签名验证。审计结果采用结构化输出(JSON/XML)避免解析漏洞。关键操作需要多因素确认，如删除敏感审计数据需二次授权。

**数据层防御**：审计报告采用AES-256-GCM加密存储，密钥托管于硬件安全模块(HSM)或操作系统密钥链。实施数据分级分类，识别并标记PII (个人身份信息)和敏感系统数据。建立数据保留策略，自动清理超过合规要求的旧审计数据。

**身份与访问控制**：基于角色的访问控制(RBAC)，区分审计员、管理员、查看者角色。实施最小权限原则，审计服务账户仅拥有执行检查所需的最低权限。定期轮换审计服务凭证，使用短期令牌替代长期API密钥。所有审计操作记录到不可篡改日志，支持行为分析检测异常访问模式。

### 3. Zero Trust (零信任)

零信任架构要求"永不信任，始终验证"，本Skill需实施以下零信任原则：

**身份验证强化**：审计系统访问实施多因素认证(MFA)，支持TOTP、FIDO2安全密钥。短期会话令牌，默认1小时过期，敏感操作需重新认证。设备信任验证，检查设备 posture (合规性、安全状态) 后才允许执行审计。实施连续身份验证，基于行为生物识别检测异常操作模式。

**最小权限访问**：审计服务按模块细分权限，网络扫描模块无需访问文件系统检查数据。动态权限提升，仅在需要时申请额外权限，使用后立即释放。实施Just-In-Time (JIT) 访问，管理员需在指定时间窗口内申请审计系统访问权限。权限使用监控，检测偏离基线的权限使用模式。

**微分段隔离**：审计系统各组件部署在独立安全域，使用服务网格进行通信。审计数据库与报告生成器网络隔离，通过API网关受控访问。实施工作负载身份，每个审计模块拥有独立服务账户和凭证。网络策略限制东-西流量，仅允许必需的组件间通信。

**持续验证与监控**：实时审计审计系统本身，检测对自身配置或数据的未授权访问。实施异常检测，使用机器学习识别异常审计模式（如非工作时间大量数据导出）。威胁情报集成，将审计结果与已知IOC (失陷指标)比对。持续合规监控，自动化验证审计系统是否符合安全基线。

**假设失陷设计**：审计数据异地备份，防止单点故障导致审计证据丢失。实施"突破检测"机制，假设攻击者已入侵，设置蜜罐审计数据诱捕内部威胁。快速轮换策略，定期更换审计服务凭证和加密密钥。事件响应自动化，检测到威胁时自动隔离受影响的审计组件。

### 4. Risk Assessment (风险评估)

基于NIST SP 800-30风险评估框架，对Security Check Skill进行定量和定性风险分析：

**威胁识别与频率评估**：
- 高风险：审计脚本被篡改注入恶意代码 (概率: 中，影响: 严重) - 风险值: 高
- 高风险：审计报告泄露敏感系统信息 (概率: 中高，影响: 高) - 风险值: 高
- 中风险：审计扫描导致生产系统性能降级 (概率: 中，影响: 中) - 风险值: 中
- 中风险：CIS基准规则误报导致不当配置 (概率: 低，影响: 中) - 风险值: 中低
- 低风险：审计日志存储耗尽磁盘空间 (概率: 中，影响: 低) - 风险值: 低

**脆弱性评估**：
- 关键脆弱性：审计引擎以高权限运行，存在权限提升攻击面
- 高危脆弱性：配置文件解析缺乏严格输入验证，可能存在注入攻击
- 中危脆弱性：审计结果存储依赖文件系统权限，存在绕过可能
- 低危脆弱性：审计报告缺少数字签名，完整性难以验证

**风险矩阵与优先级**：
```
影响\概率   很低   低    中    高    很高
严重        中    高    高    严重  严重
高          低    中    高    高    严重
中          低    低    中    中    高
低          很低  低    低    中    中
```

**风险处置策略**：
- 风险规避：移除不必要的审计功能，减少攻击面
- 风险转移：购买网络安全保险，覆盖审计数据泄露责任
- 风险缓解：实施本分析中的安全控制措施
- 风险接受：低风险项目经管理层批准后接受

**持续风险监控**：建立风险指标(KRI)，如审计系统异常访问次数、报告下载量异常等。季度风险评估回顾，根据威胁环境变化调整风险评级。

### 5. Compliance Framework (合规框架)

Security Check Skill需满足多维度合规要求，支持企业安全治理：

**CIS Controls (前5项关键控制)**：
- CIS Control 1 (资产清单)：审计模块枚举所有系统账户、服务、开放端口
- CIS Control 2 (软件授权)：检测未授权软件安装，验证软件完整性
- CIS Control 3 (数据保护)：审计数据分类标记，加密存储验证
- CIS Control 4 (安全配置)：CIS基准自动检查与加固建议
- CIS Control 5 (账户管理)：检测默认账户、共享账户、过期账户

**ISO/IEC 27001:2022 Annex A控制**：
- A.5.7 (威胁情报)：集成外部威胁情报源到审计规则
- A.8.9 (配置管理)：自动化配置基线检查与偏离检测
- A.8.11 (数据 masking)：审计报告中敏感数据自动脱敏
- A.8.16 (监控活动)：审计活动本身作为监控活动记录
- A.8.24 (渗透测试)：提供基础漏洞扫描支撑渗透测试

**NIST Cybersecurity Framework 2.0**：
- 识别(ID)：系统资产发现、漏洞识别、风险评估
- 保护(PR)：访问控制、数据安全、安全配置
- 检测(DE)：异常行为检测、持续监控
- 响应(RS)：事件响应支撑、取证数据收集
- 恢复(RC)：备份验证、恢复能力评估

**GDPR数据保护要求**：
- 数据最小化：审计仅收集必要的系统信息
- 目的限制：明确审计数据仅用于安全目的
- 存储限制：自动清理超期的审计日志
- 数据主体权利：支持审计数据查询与删除请求

**行业特定合规**：
- PCI DSS：支付卡环境安全配置审计
- HIPAA：医疗系统访问控制审计
- SOX：财务系统变更控制审计
- 等保2.0：中国网络安全等级保护测评支撑

---

## 参考标准

### CIS Benchmarks
- **CIS Windows 10/11**: https://www.cisecurity.org/benchmark/microsoft_windows_desktop
- **CIS Windows Server**: https://www.cisecurity.org/benchmark/microsoft_windows_server
- **CIS Linux**: https://www.cisecurity.org/benchmark/distribution_independent_linux

### 开源工具
- **Lynis**: https://cisofy.com/lynis/ - Linux审计工具
- **OpenVAS**: https://www.greenbone.net/openvas - 漏洞扫描
- **Windows-Debug**: https://github.com/PowerShell/SecurityPolicyDSC

### 安全框架
- **NIST SP 800-53**: 安全和隐私控制
- **ISO/IEC 27001**: 信息安全管理
- **MITRE ATT&CK**: 威胁框架

---

## 版本信息

- **Version**: 2.1.0 (安全分析增强版)
- **Author**: KbotGenesis
- **Standards**: CIS Benchmarks v8.0, CVSS v3.1, NIST SP 800-53
- **License**: MIT
- **Last Security Review**: 2026-02-19
