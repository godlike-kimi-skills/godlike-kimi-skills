# Pre-Operation Backup 快速开始

## 1. 基本使用

### 手动创建操作前备份
```bash
# 标准备份（推荐）
python ~/.kimi/skills/pre-operation-backup/scripts/backup.py create

# 轻量备份（快速操作）
python ~/.kimi/skills/pre-operation-backup/scripts/backup.py create --level light

# 完整备份（重大变更）
python ~/.kimi/skills/pre-operation-backup/scripts/backup.py create --level full --reason "删除多个skills"
```

### 查看所有快照
```bash
python ~/.kimi/skills/pre-operation-backup/scripts/backup.py list
```

### 恢复到最后一次快照
```bash
python ~/.kimi/skills/pre-operation-backup/scripts/backup.py restore
```

## 2. 自动保护模式

### 启用自动保护
```bash
python ~/.kimi/skills/pre-operation-backup/scripts/backup.py config --enable
```

### 检查操作是否危险
```bash
python ~/.kimi/skills/pre-operation-backup/scripts/backup.py check "删除 crypto-wallet skill"
# 如果是危险操作，返回 exit code 1
```

### 自动保护执行
```bash
python ~/.kimi/skills/pre-operation-backup/scripts/backup.py auto-protect "批量删除文件"
# 如果是危险操作，自动创建快照
```

## 3. 在其他脚本中集成

### PowerShell 脚本集成
```powershell
# 在危险操作前调用
$backupScript = "$env:USERPROFILE\.kimi\skills\pre-operation-backup\scripts\backup.py"
& python $backupScript create --level standard --reason "修改系统配置"

# 执行危险操作
# ... your dangerous code here ...

# 如果出错，可以恢复
# & python $backupScript restore
```

### Python 脚本集成
```python
import subprocess

# 操作前备份
subprocess.run([
    "python", 
    "~/.kimi/skills/pre-operation-backup/scripts/backup.py",
    "create",
    "--level", "standard",
    "--reason", "删除skill"
])

# 执行危险操作
# ...

# 如有需要，恢复
# subprocess.run(["python", "backup.py", "restore"])
```

## 4. 危险操作自动检测

以下关键词会触发自动备份：
- `delete skill`, `remove skill`
- `rm -rf`, `del /f`
- `git reset`, `git clean`
- `format`, `批量删除`

## 5. 快照级别说明

| 级别 | 备份内容 | 耗时 | 保留时间 |
|------|---------|------|---------|
| **light** | P0关键文件 (config.toml, MEMORY.md) | <1秒 | 24小时 |
| **standard** | 配置 + Memory + Isolator | 3-5秒 | 7天 |
| **full** | 整个.kimi目录 | 10-30秒 | 30天 |

## 6. 最佳实践

1. **常规操作** → 使用 `standard` 级别
2. **快速测试** → 使用 `light` 级别
3. **重大变更** → 使用 `full` 级别 + 明确reason
4. **脚本集成** → 在危险操作前始终调用

## 7. 恢复流程

```bash
# 1. 查看可用快照
python backup.py list

# 2. 恢复到指定快照
python backup.py restore --name pre-op-20260219-120530-standard

# 3. 或者恢复到最新
python backup.py restore
```

## 8. 配置

```bash
# 查看当前配置
python backup.py config

# 修改默认级别
python backup.py config --level full

# 禁用自动保护（不推荐）
python backup.py config --disable
```
