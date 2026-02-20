# Password Manager

**安全凭证管理系统** - 基于现代密码学最佳实践

密码生成、加密存储、安全检索、自动填充，保护数字身份安全。

---

## 核心安全架构

### 🔐 加密体系

```
数据保护流程:
明文密码 → AES-256-GCM 加密 → 存储
                ↑
         主密码 + Argon2id → 密钥派生
```

| 组件 | 算法 | 说明 |
|------|------|------|
| **对称加密** | AES-256-GCM | 数据加密 |
| **密钥派生** | Argon2id | 抵抗暴力破解 |
| **哈希** | SHA-256 | 数据完整性 |
| **随机数** | CSPRNG | 盐值生成 |

### 🛡️ 安全原则

```
1. 零知识架构
   - 服务提供商无法访问用户密码
   - 所有加密在本地完成
   
2. 主密码保护
   - 唯一需要记忆的密码
   - 永不存储、永不传输
   
3. 安全存储
   - 加密数据库本地存储
   - 可选云同步 (端到端加密)
   
4. 多因素认证
   - TOTP 支持
   - 硬件密钥 (FIDO2/WebAuthn)
```

---

## 使用方法

### CLI 命令

```bash
# 初始化密码库
password-manager init --vault ~/secure/passwords.db

# 添加密码
password-manager add \
  --name "github" \
  --username "myuser" \
  --password "generated" \
  --url "https://github.com" \
  --tags "dev,important"

# 生成强密码
password-manager generate --length 20 --symbols --copy

# 检索密码
password-manager get github --copy  # 复制到剪贴板
password-manager get github --show  # 显示明文

# 列出所有条目
password-manager list --tags dev --format table

# 更新密码
password-manager update github --password "newpassword"

# 删除条目
password-manager remove github

# 导入/导出
password-manager import --file bitwarden_export.csv --format bitwarden
password-manager export --output backup.json --encrypt

# 检查密码强度
password-manager audit --check-breach --check-reuse
```

### Python API

```python
from password_manager import Vault, PasswordGenerator

# 打开密码库
vault = Vault('~/secure/passwords.db')
vault.unlock(master_password)

# 添加条目
vault.add(
    name='aws-console',
    username='admin@company.com',
    password='...',
    url='https://console.aws.amazon.com',
    notes='Production account',
    totp_secret='JBSWY3DPEHPK3PXP'  # 2FA
)

# 检索条目
entry = vault.get('aws-console')
print(entry.password)  # 自动复制或显示

# 生成密码
gen = PasswordGenerator()
password = gen.generate(
    length=16,
    uppercase=True,
    lowercase=True,
    digits=True,
    symbols=True,
    exclude_ambiguous=True  # 排除 0/O, 1/l
)

# 锁定
vault.lock()
```

---

## 高级功能

### 密码生成策略

| 场景 | 配置 | 示例 |
|------|------|------|
| **通用** | 16位, 混合 | `Tr0ub4dor&3` |
| **高安全** | 20位, 全字符 | `xK9#mP2$vL5@nQ8*wJ4` |
| **易读** | 4词组 | `correct-horse-battery-staple` |
| **PIN** | 6-8位数字 | `837291` |
| **密钥** | 32字节 base64 | `aB3xK9mP2vL5nQ8w...` |

### 安全审计

```bash
# 密码健康检查
password-manager audit

# 检查项目
Auditing vault:
├── Weak passwords: 3 found
├── Reused passwords: 2 found
├── Old passwords (>1y): 5 found
├── Breached passwords: 0 found ✓
└── Missing 2FA: 10 found

# 生成报告
password-manager report --output security_report.html
```

### 自动填充

```python
# 浏览器集成 (需扩展)
from password_manager import BrowserIntegration

browser = BrowserIntegration()
browser.autofill(
    url='https://github.com/login',
    username_field='login',
    password_field='password'
)
```

---

## 数据同步

### 云同步选项

| 方案 | 加密 | 便利性 | 风险 |
|------|------|--------|------|
| **本地** | 本地密钥 | 低 | 数据丢失风险 |
| **自托管** | 端到端加密 | 中 | 需技术能力 |
| **云服务** | 端到端加密 | 高 | 信任服务商 |

### 同步配置

```yaml
# config.yml
sync:
  provider: webdav  # s3, dropbox, nextcloud
  endpoint: https://myserver.com/webdav
  interval: 3600  # 秒
  conflict_resolution: newest  # newest, manual
  
encryption:
  master_key_derivation: argon2id
  data_encryption: aes-256-gcm
```

---

## 备份与恢复

### 备份策略

```bash
# 自动备份
password-manager backup --auto --retention 30

# 导出加密备份
password-manager export \
  --output backup_$(date +%Y%m%d).enc \
  --encrypt-with-passphrase

# 紧急恢复表
password-manager emergency-sheet --print
```

### 恢复流程

```bash
# 从备份恢复
password-manager restore --file backup.enc

# 从其他管理器导入
password-manager import --file export.csv --format bitwarden
password-manager import --file export.json --format 1password
```

---

## 最佳实践

### 主密码建议

```
✅ 好的主密码:
├── 至少 12 个字符
├── 混合大小写、数字、符号
├── 不基于个人信息
├── 使用密码短语
└── 示例: "Coffee-At-9AM-With-Milk!"

❌ 避免:
├── 短密码 (< 8字符)
├── 常见单词
├── 键盘序列 (qwerty)
└── 个人信息
```

### 日常使用

```
1. 为每个服务使用唯一密码
2. 启用双因素认证 (2FA)
3. 定期审查密码安全
4. 及时更新泄露密码
5. 安全备份密码库
```

---

## 参考来源

- **Bitwarden**: 开源密码管理器
- **KeePass**: 本地密码管理
- **OWASP**: 密码安全指南
- **NIST**: 数字身份指南

---

## 版本信息

- **Version**: 2.0.0 (2025 增强版)
- **Author**: KbotGenesis
- **Last Updated**: 2026-02-19
