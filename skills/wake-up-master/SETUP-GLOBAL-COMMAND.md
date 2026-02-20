# Wake Up Master - 全局命令配置指南

配置完成后，你可以在任何地方输入 `wake up` 来执行唤醒流程。

---

## 快速配置（自动）

运行以下命令自动配置：

```powershell
# 添加 wake 函数到 PowerShell Profile
$profileContent = @'
# Wake Up Master - Global Command
function wake {
    param(
        [Parameter(Position = 0)]
        [string]$Command = "up",
        
        [switch]$quick,
        [switch]$update,
        [switch]$security,
        [switch]$tasks,
        [switch]$repair,
        [switch]$help
    )
    
    & "$env:USERPROFILE\.kimi\scripts\wake.ps1" @PSBoundParameters
}

# Alias for convenience
Set-Alias -Name "wakeup" -Value wake
'@

Add-Content -Path $PROFILE -Value $profileContent
Write-Host "Configuration added to PowerShell Profile"
Write-Host "Restart PowerShell or run '. `$PROFILE' to activate"
```

---

## 手动配置

### 1. 编辑 PowerShell Profile

```powershell
# 打开配置文件
if (-not (Test-Path $PROFILE)) {
    New-Item -ItemType File -Path $PROFILE -Force
}
notepad $PROFILE
```

### 2. 添加以下内容

```powershell
# ═══════════════════════════════════════════════════════════
# Wake Up Master - Global Command Configuration
# ═══════════════════════════════════════════════════════════

function wake {
    <#
    .SYNOPSIS
        Global wake up command for Kimi system
    .DESCRIPTION
        Can be called from anywhere with: wake up [options]
    #>
    param(
        [Parameter(Position = 0)]
        [string]$Command = "up",
        
        [switch]$quick,
        [switch]$update,
        [switch]$security,
        [switch]$tasks,
        [switch]$repair,
        [switch]$help
    )
    
    & "$env:USERPROFILE\.kimi\scripts\wake.ps1" @PSBoundParameters
}

# Optional: Create shorter alias
Set-Alias -Name "wakeup" -Value wake
Set-Alias -Name "w" -Value wake
```

### 3. 重新加载配置

```powershell
. $PROFILE
```

---

## 使用方式

配置完成后，在任何 PowerShell 窗口中都可以使用：

```bash
# 完整唤醒（13阶段）
wake up

# 快速模式（5阶段）
wake up --quick

# 专注安全扫描
wake up --security

# 专注任务报告
wake up --tasks

# 专注Skills更新
wake up --update

# 显示帮助
wake up --help
```

---

## 命令对比

| 命令 | 等效调用 | 说明 |
|------|----------|------|
| `wake up` | `execute-v2.ps1` | 完整13阶段 |
| `wake up --quick` | `wake-up-simple.ps1` | 快速5阶段 |
| `wake up --security` | `execute-v2.ps1 -SkipSkillsUpdate -SkipTaskReport` | 专注安全 |
| `wake up --tasks` | `execute-v2.ps1 -SkipSecurity -SkipSkillsUpdate` | 专注任务 |

---

## 故障排除

### 命令未找到

```powershell
# 检查函数是否加载
Get-Command wake

# 如果没有，手动加载
. "$env:USERPROFILE\.kimi\scripts\wake.ps1"
```

### 权限问题

```powershell
# 检查脚本执行策略
Get-ExecutionPolicy

# 设置为 RemoteSigned（如果为 Restricted）
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 路径问题

```powershell
# 验证路径存在
Test-Path "$env:USERPROFILE\.kimi\scripts\wake.ps1"
Test-Path "$env:USERPROFILE\.kimi\skills\wake-up-master\scripts\execute-v2.ps1"
```

---

## 13阶段 vs 5阶段对比

| 功能 | 完整模式 (13阶段) | 快速模式 (5阶段) |
|------|-------------------|------------------|
| 系统健康检查 | ✅ | ✅ |
| 环境验证 | ✅ | ✅ |
| **安全隐私扫描** | ✅ | ❌ |
| **Skills可用性检查** | ✅ | ❌ |
| **Skills更新检查** | ✅ | ❌ |
| 备份同步 | ✅ | ✅ |
| 内存加载 | ✅ | ✅ |
| Git同步 | ✅ | ❌ |
| Hooks初始化 | ✅ | ❌ |
| Agent生态同步 | ✅ | ❌ |
| **Agent Bus同步** | ✅ | ❌ |
| **任务状态报告** | ✅ | ❌ |
| 就绪报告 | ✅ | ✅ |
| **预计耗时** | 3-5分钟 | 10-20秒 |

---

## 推荐的日常使用流程

### 早晨开机
```bash
wake up --quick    # 快速检查系统状态
```

### 开始重要工作前
```bash
wake up --security  # 确保环境安全
```

### 每日结束工作
```bash
wake up            # 完整检查并备份
```

### 每周维护
```bash
wake up --update   # 检查Skills更新
```
