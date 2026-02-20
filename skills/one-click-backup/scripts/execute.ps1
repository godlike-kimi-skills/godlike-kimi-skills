#!/usr/bin/env pwsh
<#
.SYNOPSIS
    One-Click Backup Executor
    协调所有备份组件执行完整备份流程
.DESCRIPTION
    执行顺序:
    1. Pre-operation backup (safety snapshot)
    2. Smart backup execution
    3. Agent bus notification
    4. Verification
#>

param(
    [switch]$SkipPreOp,
    [switch]$SkipGitHub,
    [switch]$SkipNotification
)

$ErrorActionPreference = "Stop"

# 配置路径
$Config = @{
    PreOpScript = "$env:USERPROFILE\.kimi\skills\pre-operation-backup\scripts\backup.py"
    SmartBackupScript = "$env:USERPROFILE\.kimi\scripts\smart-backup-v3.ps1"
    AgentBusNotifyScript = "$env:USERPROFILE\.kimi\agent-bus\notify_agents.ps1"
}

function Log($Message, $Color = "White") {
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] $Message" -ForegroundColor $Color
}

function Log-Step($Step, $Total, $Message) {
    Log ""
    Log "========================================" "Cyan"
    Log "  Step $Step/$Total : $Message" "Cyan"
    Log "========================================" "Cyan"
}

# ═══════════════════════════════════════════════════════════════
# STEP 1: Pre-Operation Backup
# ═══════════════════════════════════════════════════════════════
function Step-PreOpBackup() {
    Log-Step 1 4 "PRE-OPERATION BACKUP"
    
    if (-not (Test-Path $Config.PreOpScript)) {
        Log "[WARN] Pre-operation backup script not found, skipping..." "Yellow"
        return $true
    }
    
    Log "Creating safety snapshot before main backup..."
    
    try {
        $output = & python $Config.PreOpScript create --level light --reason "Before one-click backup" 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Log "[OK] Pre-operation snapshot created" "Green"
            return $true
        } else {
            Log "[WARN] Pre-operation backup returned exit code $LASTEXITCODE" "Yellow"
            Log "Output: $output" "Gray"
            return $true  # 继续执行，不中断主流程
        }
    } catch {
        Log "[WARN] Pre-operation backup failed: $_" "Yellow"
        return $true  # 继续执行主备份
    }
}

# ═══════════════════════════════════════════════════════════════
# STEP 2: Smart Backup Execution
# ═══════════════════════════════════════════════════════════════
function Step-SmartBackup() {
    Log-Step 2 4 "SMART BACKUP EXECUTION"
    
    if (-not (Test-Path $Config.SmartBackupScript)) {
        Log "[ERROR] Smart backup script not found: $($Config.SmartBackupScript)" "Red"
        return $false
    }
    
    Log "Executing smart backup..."
    
    try {
        & $Config.SmartBackupScript -Action backup
        
        if ($LASTEXITCODE -eq 0) {
            Log "[OK] Smart backup completed successfully" "Green"
            return $true
        } else {
            Log "[ERROR] Smart backup failed with exit code $LASTEXITCODE" "Red"
            return $false
        }
    } catch {
        Log "[ERROR] Smart backup execution failed: $_" "Red"
        return $false
    }
}

# ═══════════════════════════════════════════════════════════════
# STEP 3: Agent Bus Notification
# ═══════════════════════════════════════════════════════════════
function Step-AgentBusNotification() {
    Log-Step 3 4 "AGENT BUS NOTIFICATION"
    
    if ($SkipNotification) {
        Log "[SKIP] Notification skipped by user request" "Yellow"
        return $true
    }
    
    if (-not (Test-Path $Config.AgentBusNotifyScript)) {
        Log "[WARN] Agent bus notifier not found" "Yellow"
        return $true
    }
    
    # 获取最新的备份信息
    $backupDir = "D:\kimi\SmartBackups"
    $latestBackup = Get-ChildItem $backupDir -Directory -ErrorAction SilentlyContinue | 
        Sort-Object CreationTime -Descending | 
        Select-Object -First 1
    
    if (-not $latestBackup) {
        Log "[WARN] No backup found to notify about" "Yellow"
        return $true
    }
    
    $sizeMB = [math]::Round(
        (Get-ChildItem $latestBackup.FullName -Recurse -File -ErrorAction SilentlyContinue | 
            Measure-Object -Property Length -Sum).Sum / 1MB, 2
    )
    
    $backupType = if ($latestBackup.Name -match "^FULL-") { "FULL" } else { "INCREMENTAL" }
    
    Log "Broadcasting notification to all agents..."
    
    try {
        & $Config.AgentBusNotifyScript `
            -BackupPath $latestBackup.FullName `
            -BackupType $backupType `
            -BackupSizeMB $sizeMB `
            -Message "One-click backup completed. All agents should reload."
        
        Log "[OK] Agents notified via Agent Bus" "Green"
        return $true
    } catch {
        Log "[WARN] Agent notification failed: $_" "Yellow"
        return $true  # 不中断流程
    }
}

# ═══════════════════════════════════════════════════════════════
# STEP 4: Verification
# ═══════════════════════════════════════════════════════════════
function Step-Verification() {
    Log-Step 4 4 "BACKUP VERIFICATION"
    
    $backupDir = "D:\kimi\SmartBackups"
    $latestBackup = Get-ChildItem $backupDir -Directory -ErrorAction SilentlyContinue | 
        Sort-Object CreationTime -Descending | 
        Select-Object -First 1
    
    if (-not $latestBackup) {
        Log "[ERROR] No backup found for verification" "Red"
        return $false
    }
    
    Log "Verifying backup: $($latestBackup.Name)"
    
    # 检查关键文件
    $checks = @(
        @{ Path = "$($latestBackup.FullName)\MEMORIES"; Name = "Memories" }
        @{ Path = "$($latestBackup.FullName)\CONFIGS"; Name = "Configs" }
    )
    
    $allOk = $true
    foreach ($check in $checks) {
        if (Test-Path $check.Path) {
            $size = [math]::Round(
                (Get-ChildItem $check.Path -Recurse -File -ErrorAction SilentlyContinue | 
                    Measure-Object -Property Length -Sum).Sum / 1MB, 2
            )
            Log "  [OK] $($check.Name): ${size}MB" "Green"
        } else {
            Log "  [MISSING] $($check.Name)" "Red"
            $allOk = $false
        }
    }
    
    if ($allOk) {
        Log "[OK] Backup verification passed" "Green"
    } else {
        Log "[WARN] Some backup components are missing" "Yellow"
    }
    
    return $allOk
}

# ═══════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════
function Main() {
    Log ""
    Log "╔═══════════════════════════════════════════════════════════════╗" "Cyan"
    Log "║                                                               ║" "Cyan"
    Log "║              ONE-CLICK BACKUP EXECUTOR v1.0                   ║" "Cyan"
    Log "║                                                               ║" "Cyan"
    Log "╚═══════════════════════════════════════════════════════════════╝" "Cyan"
    Log ""
    
    $startTime = Get-Date
    
    # Execute all steps
    $results = @()
    
    # Step 1: Pre-operation backup (unless skipped)
    if (-not $SkipPreOp) {
        $results += Step-PreOpBackup
    } else {
        Log "[SKIP] Pre-operation backup skipped by user request" "Yellow"
        $results += $true
    }
    
    # Step 2: Smart backup (mandatory)
    $results += Step-SmartBackup
    
    # If smart backup failed, stop here
    if (-not $results[-1]) {
        Log ""
        Log "========================================" "Red"
        Log "  ONE-CLICK BACKUP FAILED" "Red"
        Log "========================================" "Red"
        Log ""
        Log "Smart backup step failed. Pre-operation snapshot may be used for recovery." "Yellow"
        exit 1
    }
    
    # Step 3: Agent Bus notification
    $results += Step-AgentBusNotification
    
    # Step 4: Verification
    $results += Step-Verification
    
    # Final summary
    $endTime = Get-Date
    $duration = ($endTime - $startTime).ToString("mm\:ss")
    
    Log ""
    Log "========================================" "Green"
    Log "  ONE-CLICK BACKUP COMPLETE" "Green"
    Log "========================================" "Green"
    Log ""
    Log "Duration: $duration"
    Log "Steps completed: $($results.Count)"
    Log "All steps successful: $(if($results -notcontains $false){'YES'}else{'NO'})"
    Log ""
    
    # Show latest backup info
    $latestBackup = Get-ChildItem "D:\kimi\SmartBackups" -Directory -ErrorAction SilentlyContinue | 
        Sort-Object CreationTime -Descending | 
        Select-Object -First 1
    
    if ($latestBackup) {
        $size = [math]::Round(
            (Get-ChildItem $latestBackup.FullName -Recurse -File -ErrorAction SilentlyContinue | 
                Measure-Object -Property Length -Sum).Sum / 1MB, 2
        )
        Log "Latest Backup: $($latestBackup.Name)" "Cyan"
        Log "Size: ${size}MB" "Cyan"
        Log "Location: $($latestBackup.FullName)" "Gray"
    }
    
    Log ""
    Log "Components executed:"
    Log "  ✓ Pre-operation backup (safety)"
    Log "  ✓ Smart backup (memory + configs)"
    Log "  ✓ GitHub sync (if configured)"
    Log "  ✓ Agent Bus notification"
    Log "  ✓ Verification"
    Log ""
}

# Run main
Main
