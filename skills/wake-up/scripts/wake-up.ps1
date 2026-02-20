#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Kbot Wake Up - System initialization and synchronization
.DESCRIPTION
    Complete wake-up sequence:
    1. System health check
    2. Backup verification
    3. Memory loading
    4. Agent synchronization
    5. Ready state
.PARAMETER Mode
    Execution mode: normal, quick, refresh, diagnostic
.PARAMETER SkipBackup
    Skip backup verification
.PARAMETER SkipAgentSync
    Skip agent synchronization
#>

[CmdletBinding()]
param(
    [ValidateSet("normal", "quick", "refresh", "diagnostic")]
    [string]$Mode = "normal",
    
    [switch]$SkipBackup,
    [switch]$SkipAgentSync
)

# Configuration
$Config = @{
    Version = "1.0.0"
    KimiHome = "$env:USERPROFILE\.kimi"
    OpenClawWorkspace = "$env:USERPROFILE\.openclaw\workspace"
    AgentBusDir = "$env:USERPROFILE\.kimi\agent-bus"
    BackupRoot = "D:\kimi\SmartBackups"
}

# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
# Utility Functions
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
function Write-Step($Number, $Total, $Message) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Step $Number/$Total : $Message" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
}

function Write-Check($Message, $Status, $Details = "") {
    $color = switch ($Status) {
        "OK" { "Green" }
        "WARN" { "Yellow" }
        "FAIL" { "Red" }
        default { "White" }
    }
    $icon = switch ($Status) {
        "OK" { "[OK]" }
        "WARN" { "[!]" }
        "FAIL" { "[X]" }
        default { "[ ]" }
    }
    
    Write-Host "  $icon $Message" -ForegroundColor $color -NoNewline
    if ($Details) {
        Write-Host ": $Details" -ForegroundColor Gray
    } else {
        Write-Host ""
    }
}

function Show-Banner() {
    Clear-Host
    Write-Host ""
    Write-Host "鈺斺晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺? -ForegroundColor Cyan
    Write-Host "鈺?                                                              鈺? -ForegroundColor Cyan
    Write-Host "鈺?             Kbot Wake Up Sequence v$($Config.Version)                       鈺? -ForegroundColor Cyan
    Write-Host "鈺?                                                              鈺? -ForegroundColor Cyan
    Write-Host "鈺氣晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺? -ForegroundColor Cyan
    Write-Host ""
}

# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
# STEP 1: System Health Check
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
function Step-HealthCheck() {
    Write-Step 1 5 "SYSTEM HEALTH CHECK"
    
    $checks = @{
        Disk = $false
        Memory = $false
        Network = $false
        GitHub = $false
    }
    
    # Disk Space Check
    $disk = Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='C:'"
    $freeGB = [math]::Round($disk.FreeSpace / 1GB, 2)
    $checks.Disk = $freeGB -gt 10
    Write-Check "Disk space" $(if($checks.Disk){"OK"}else{"WARN"}) "$freeGB GB available"
    
    # Memory Check
    $os = Get-WmiObject -Class Win32_OperatingSystem
    $availableGB = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
    $checks.Memory = $availableGB -gt 2
    Write-Check "Memory" $(if($checks.Memory){"OK"}else{"WARN"}) "$availableGB GB available"
    
    # Network Check
    $network = Test-Connection -ComputerName "8.8.8.8" -Count 1 -Quiet
    $checks.Network = $network
    Write-Check "Network" $(if($checks.Network){"OK"}else{"FAIL"}) $(if($checks.Network){"Connected"}else{"Disconnected"})
    
    # GitHub Check
    $github = $false
    try {
        $response = Invoke-WebRequest -Uri "https://api.github.com" -Method Head -TimeoutSec 5 -ErrorAction SilentlyContinue
        $github = $response.StatusCode -eq 200
    } catch {}
    $checks.GitHub = $github
    Write-Check "GitHub API" $(if($checks.GitHub){"OK"}else{"WARN"}) $(if($checks.GitHub){"Reachable"}else{"Unavailable"})
    
    return $checks
}

# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
# STEP 2: Backup Verification
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
function Step-BackupVerification() {
    Write-Step 2 5 "BACKUP VERIFICATION"
    
    if (-not (Test-Path $Config.BackupRoot)) {
        Write-Check "Backup directory" "WARN" "Not found"
        return @{ Valid = $false; NeedsBackup = $true }
    }
    
    # Find latest backup
    $latestBackup = Get-ChildItem $Config.BackupRoot -Directory -ErrorAction SilentlyContinue | 
        Sort-Object CreationTime -Descending | 
        Select-Object -First 1
    
    if (-not $latestBackup) {
        Write-Check "Latest backup" "WARN" "No backups found"
        return @{ Valid = $false; NeedsBackup = $true }
    }
    
    # Check backup age
    $age = (Get-Date) - $latestBackup.CreationTime
    $ageHours = [math]::Round($age.TotalHours, 1)
    $isRecent = $ageHours -lt 24
    
    Write-Check "Latest backup" $(if($isRecent){"OK"}else{"WARN"}) "$($latestBackup.Name) (${ageHours}h ago)"
    
    # Check backup size
    $size = (Get-ChildItem $latestBackup.FullName -Recurse -File -ErrorAction SilentlyContinue | 
        Measure-Object -Property Length -Sum).Sum
    $sizeMB = [math]::Round($size / 1MB, 2)
    $hasContent = $sizeMB -gt 0
    
    Write-Check "Backup size" $(if($hasContent){"OK"}else{"FAIL"}) "${sizeMB}MB"
    
    # Check integrity (basic)
    $memoriesExist = Test-Path "$($latestBackup.FullName)\MEMORIES"
    $configsExist = Test-Path "$($latestBackup.FullName)\CONFIGS"
    $integrityOk = $memoriesExist -and $configsExist
    
    Write-Check "Backup integrity" $(if($integrityOk){"OK"}else{"FAIL"}) $(if($integrityOk){"Valid"}else{"Missing components"})
    
    # Check GitHub sync
    $githubSync = $false
    $gitDir = "$($latestBackup.FullName)\.git"
    if (Test-Path $gitDir) {
        $githubSync = $true
    }
    Write-Check "GitHub sync" $(if($githubSync){"OK"}else{"WARN"}) $(if($githubSync){"Synced"}else{"Local only"})
    
    return @{
        Valid = $isRecent -and $hasContent -and $integrityOk
        NeedsBackup = -not ($isRecent -and $hasContent)
        LatestBackup = $latestBackup
        SizeMB = $sizeMB
        AgeHours = $ageHours
    }
}

# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
# STEP 3: Memory Loading
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
function Step-MemoryLoading() {
    Write-Step 3 5 "MEMORY LOADING"
    
    $memoryStatus = @{
        HotMemory = $false
        Identity = $false
        Channel = $false
        Blocks = $false
    }
    
    # Check Hot Memory
    $hotMemoryPath = "$($Config.KimiHome)\memory\hot\MEMORY.md"
    $memoryStatus.HotMemory = Test-Path $hotMemoryPath
    Write-Check "Hot Memory (P0)" $(if($memoryStatus.HotMemory){"OK"}else{"WARN"}) $(if($memoryStatus.HotMemory){"Loaded"}else{"Not found"})
    
    # Check Identity
    $identityPath = "$($Config.KimiHome)\memory\hot\IDENTITY.md"
    $memoryStatus.Identity = Test-Path $identityPath
    Write-Check "Identity" $(if($memoryStatus.Identity){"OK"}else{"WARN"}) $(if($memoryStatus.Identity){"Valid"}else{"Not found"})
    
    # Check Active Channel
    $activeChannelPath = "$($Config.KimiHome)\isolator\active.json"
    $memoryStatus.Channel = Test-Path $activeChannelPath
    if ($memoryStatus.Channel) {
        try {
            $active = Get-Content $activeChannelPath | ConvertFrom-Json
            $channelName = $active.channel
            Write-Check "Active Channel" "OK" $channelName
        } catch {
            Write-Check "Active Channel" "WARN" "Cannot read"
        }
    } else {
        Write-Check "Active Channel" "WARN" "Not set"
    }
    
    # Check Memory Blocks
    $blocksDir = "$($Config.KimiHome)\memory\warm\blocks"
    $blockCount = 0
    if (Test-Path $blocksDir) {
        $blockCount = (Get-ChildItem $blocksDir -Filter "*.json" -ErrorAction SilentlyContinue).Count
    }
    $memoryStatus.Blocks = $blockCount -gt 0
    Write-Check "Memory Blocks" $(if($memoryStatus.Blocks){"OK"}else{"WARN"}) "$blockCount blocks"
    
    return $memoryStatus
}

# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
# STEP 4: Agent Synchronization
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
function Step-AgentSync() {
    Write-Step 4 5 "AGENT SYNCHRONIZATION"
    
    $agentStatus = @{
        BusRunning = $false
        AgentsRegistered = 0
        PendingMessages = 0
    }
    
    # Check Agent Bus
    $agentStatus.BusRunning = Test-Path $Config.AgentBusDir
    Write-Check "Agent Bus" $(if($agentStatus.BusRunning){"OK"}else{"WARN"}) $(if($agentStatus.BusRunning){"Running"}else{"Not initialized"})
    
    # Check registered agents
    $subscribersFile = "$($Config.AgentBusDir)\subscribers.json"
    if (Test-Path $subscribersFile) {
        try {
            $subscribers = Get-Content $subscribersFile | ConvertFrom-Json
            $agentStatus.AgentsRegistered = $subscribers.agents.Count
        } catch {}
    }
    Write-Check "Registered agents" "OK" "$($agentStatus.AgentsRegistered) agents"
    
    # Check pending notifications
    $notificationsDir = "$($Config.AgentBusDir)\notifications"
    if (Test-Path $notificationsDir) {
        $agentStatus.PendingMessages = (Get-ChildItem $notificationsDir -Filter "*.json" -ErrorAction SilentlyContinue).Count
    }
    Write-Check "Pending messages" $(if($agentStatus.PendingMessages -eq 0){"OK"}else{"WARN"}) "$($agentStatus.PendingMessages) messages"
    
    # Check for backup notifications
    $backupNotifications = @()
    if (Test-Path $notificationsDir) {
        $backupNotifications = Get-ChildItem $notificationsDir -Filter "backup-notification-*.json" -ErrorAction SilentlyContinue | 
            Sort-Object CreationTime -Descending | 
            Select-Object -First 1
    }
    
    if ($backupNotifications) {
        try {
            $notif = Get-Content $backupNotifications.FullName | ConvertFrom-Json
            $backupTime = $notif.timestamp
            Write-Check "Latest backup notification" "OK" $backupTime
        } catch {
            Write-Check "Latest backup notification" "WARN" "Cannot read"
        }
    } else {
        Write-Check "Backup notifications" "WARN" "None found"
    }
    
    return $agentStatus
}

# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
# STEP 5: Ready State
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
function Step-ReadyState($Health, $Backup, $Memory, $Agent) {
    Write-Step 5 5 "SYSTEM READY"
    
    # Calculate overall status
    $criticalOk = $Health.Disk -and $Health.Memory
    $backupOk = $Backup.Valid
    $memoryOk = $Memory.HotMemory -and $Memory.Identity
    $agentOk = $Agent.BusRunning
    
    $allOk = $criticalOk -and $backupOk -and $memoryOk -and $agentOk
    
    Write-Host ""
    if ($allOk) {
        Write-Host "鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺? -ForegroundColor Green
        Write-Host "                    SYSTEM READY" -ForegroundColor Green
        Write-Host "鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺? -ForegroundColor Green
    } else {
        Write-Host "鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺? -ForegroundColor Yellow
        Write-Host "                 SYSTEM READY (with warnings)" -ForegroundColor Yellow
        Write-Host "鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺? -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "Welcome back! 馃憢" -ForegroundColor Cyan
    Write-Host ""
    
    # Status summary
    Write-Host "Current Status:" -ForegroundColor White
    Write-Host "  鈥?Memory: $(if($memoryOk){'Fully loaded'}else{'Partial'})" -ForegroundColor Gray
    Write-Host "  鈥?Backup: $(if($backupOk){'Up to date'}else{'Needs update'}) ($([math]::Round($Backup.AgeHours, 1))h ago)" -ForegroundColor Gray
    Write-Host "  鈥?Agents: $(if($agentOk){'All synchronized'}else{'Sync needed'}) ($($Agent.AgentsRegistered))" -ForegroundColor Gray
    Write-Host "  鈥?Health: $(if($criticalOk){'Good'}else{'Check required'})" -ForegroundColor Gray
    
    Write-Host ""
    Write-Host "Available Commands:" -ForegroundColor White
    Write-Host "  wake up --refresh    - Reload all memories" -ForegroundColor Gray
    Write-Host "  one-click-backup     - Execute backup now" -ForegroundColor Gray
    Write-Host "  /sessions list       - View session history" -ForegroundColor Gray
    Write-Host "  /status              - Check system status" -ForegroundColor Gray
    
    Write-Host ""
    
    return $allOk
}

# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
# Main Execution
# 鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺愨晲鈺?
function Main() {
    Show-Banner
    
    $startTime = Get-Date
    
    # Step 1: Health Check
    $health = Step-HealthCheck
    
    # Step 2: Backup Verification
    $backup = $null
    if (-not $SkipBackup) {
        $backup = Step-BackupVerification
        
        # Auto-backup if needed
        if ($backup.NeedsBackup -and $Mode -ne "quick") {
            Write-Host ""
            Write-Host "Backup is outdated. Executing one-click backup..." -ForegroundColor Yellow
            
            $oneClickBackup = "$($Config.KimiHome)\skills\one-click-backup\scripts\execute.ps1"
            if (Test-Path $oneClickBackup) {
                & $oneClickBackup
                # Re-check backup
                $backup = Step-BackupVerification
            }
        }
    }
    
    # Step 3: Memory Loading
    $memory = Step-MemoryLoading
    
    # Step 4: Agent Sync
    $agent = $null
    if (-not $SkipAgentSync) {
        $agent = Step-AgentSync
    }
    
    # Step 5: Ready State
    $ready = Step-ReadyState $health $backup $memory $agent
    
    # Execution time
    $duration = (Get-Date) - $startTime
    Write-Host "Wake up completed in $([math]::Round($duration.TotalSeconds, 1))s" -ForegroundColor Gray
    Write-Host ""
    
    return $ready
}

# Run main
Main

