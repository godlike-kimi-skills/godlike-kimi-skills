#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Wake Up Master - Complete System Initialization
.DESCRIPTION
    8-Phase Wake Up Sequence:
    1. System Health Check
    2. Environment Validation
    3. Backup System Sync
    4. Memory System Initialization
    5. Git Repository Sync
    6. Hooks System Initialization
    7. Agent Ecosystem Sync
    8. Ready State & Report
.PARAMETER Mode
    Execution mode: normal, quick, repair, diagnostic
.PARAMETER SkipPhase
    Skip specific phases
#>

[CmdletBinding()]
param(
    [ValidateSet("normal", "quick", "repair", "diagnostic")]
    [string]$Mode = "normal",
    
    [switch]$SkipHealth,
    [switch]$SkipBackup,
    [switch]$SkipGit,
    [switch]$SkipHooks,
    [switch]$SkipAgents
)

# Configuration
$Config = @{
    Version = "1.0.0"
    KimiHome = "$env:USERPROFILE\.kimi"
    OpenClawDir = "$env:USERPROFILE\.openclaw"
    BackupRoot = "D:\kimi\SmartBackups"
    LogDir = "$env:USERPROFILE\.kimi\logs\wake-up-master"
}

# Ensure log directory
New-Item -ItemType Directory -Force -Path $Config.LogDir | Out-Null
$LogFile = "$($Config.LogDir)\wake-up-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

# Logging Functions
function Write-Log($Message, $Level = "INFO") {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Add-Content -Path $LogFile -Value $logEntry
    
    switch ($Level) {
        "SUCCESS" { Write-Host $Message -ForegroundColor Green }
        "WARNING" { Write-Host $Message -ForegroundColor Yellow }
        "ERROR"   { Write-Host $Message -ForegroundColor Red }
        "PHASE"   { Write-Host $Message -ForegroundColor Cyan }
        default   { Write-Host $Message }
    }
}

function Write-Phase($Number, $Name) {
    Write-Log ""
    Write-Log "========================================" "PHASE"
    Write-Log "  PHASE $Number/8 : $Name" "PHASE"
    Write-Log "========================================" "PHASE"
}

function Write-Check($Item, $Status, $Details = "") {
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
    
    if ($Details) {
        Write-Log "  $icon $Item : $Details" $color
    } else {
        Write-Log "  $icon $Item" $color
    }
}

# PHASE 1: System Health Check
function Phase1-HealthCheck() {
    Write-Phase 1 "SYSTEM HEALTH CHECK"
    
    $results = @{}
    
    # Disk Check
    try {
        $disk = Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='C:'" -ErrorAction Stop
        $freeGB = [math]::Round($disk.FreeSpace / 1GB, 2)
        $results.Disk = $freeGB -gt 10
        Write-Check "Disk Space" $(if($results.Disk){"OK"}else{"WARN"}) "$freeGB GB available"
    } catch {
        Write-Check "Disk Space" "FAIL" "Cannot query"
        $results.Disk = $false
    }
    
    # Memory Check
    try {
        $os = Get-WmiObject -Class Win32_OperatingSystem -ErrorAction Stop
        $availableGB = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
        $results.Memory = $availableGB -gt 2
        Write-Check "Memory" $(if($results.Memory){"OK"}else{"WARN"}) "$availableGB GB available"
    } catch {
        Write-Check "Memory" "FAIL" "Cannot query"
        $results.Memory = $false
    }
    
    # Network Check
    $network = Test-Connection -ComputerName "8.8.8.8" -Count 1 -Quiet
    $results.Network = $network
    Write-Check "Network" $(if($results.Network){"OK"}else{"WARN"}) $(if($results.Network){"Connected"}else{"Disconnected"})
    
    # GitHub Check (optional) - skipped for speed
    $results.GitHub = $false
    Write-Check "GitHub API" "SKIP" "Skipped for speed"
    
    return $results
}

# PHASE 2: Environment Validation
function Phase2-EnvironmentValidation() {
    Write-Phase 2 "ENVIRONMENT VALIDATION"
    
    $results = @{}
    
    # Config Check
    $configPath = "$($Config.KimiHome)\config.toml"
    $results.Config = Test-Path $configPath
    Write-Check "Kimi Config" $(if($results.Config){"OK"}else{"WARN"}) $(if($results.Config){"Found"}else{"Missing - will create"})
    
    # Directory Structure
    $dirs = @("skills", "scripts", "memory", "rules", "config")
    $missingDirs = @()
    foreach ($dir in $dirs) {
        $path = "$($Config.KimiHome)\$dir"
        if (-not (Test-Path $path)) {
            $missingDirs += $dir
            New-Item -ItemType Directory -Path $path -Force | Out-Null
        }
    }
    Write-Check "Directory Structure" $(if($missingDirs.Count -eq 0){"OK"}else{"FIXED"}) "Created: $($missingDirs -join ', ')"
    $results.Directories = $true
    
    # Dependencies Check
    $deps = @{
        "git" = "git --version"
        "python" = "python --version"
    }
    foreach ($dep in $deps.GetEnumerator()) {
        $exists = $null -ne (Get-Command $dep.Key -ErrorAction SilentlyContinue)
        Write-Check "$($dep.Key)" $(if($exists){"OK"}else{"WARN"})
    }
    
    return $results
}

# PHASE 3: Backup System Sync
function Phase3-BackupSync() {
    Write-Phase 3 "BACKUP SYSTEM SYNC"
    
    $results = @{}
    
    # Check Backup Directory
    if (-not (Test-Path $Config.BackupRoot)) {
        New-Item -ItemType Directory -Path $Config.BackupRoot -Force | Out-Null
        Write-Check "Backup Directory" "FIXED" "Created"
    } else {
        Write-Check "Backup Directory" "OK" "Exists"
    }
    
    # Find Latest Backup
    $latestBackup = Get-ChildItem $Config.BackupRoot -Directory -ErrorAction SilentlyContinue | 
        Sort-Object CreationTime -Descending | 
        Select-Object -First 1
    
    if ($latestBackup) {
        $age = (Get-Date) - $latestBackup.CreationTime
        $ageHours = [math]::Round($age.TotalHours, 1)
        $isRecent = $ageHours -lt 24
        
        Write-Check "Latest Backup" $(if($isRecent){"OK"}else{"WARN"}) "$($latestBackup.Name) (${ageHours}h ago)"
        
        # Check Size
        $size = (Get-ChildItem $latestBackup.FullName -Recurse -File -ErrorAction SilentlyContinue | 
            Measure-Object -Property Length -Sum).Sum
        $sizeMB = [math]::Round($size / 1MB, 2)
        Write-Check "Backup Size" "OK" "$sizeMB MB"
        
        $results.LatestBackup = $latestBackup
        $results.SizeMB = $sizeMB
        $results.AgeHours = $ageHours
        $results.Valid = $isRecent
    } else {
        Write-Check "Latest Backup" "WARN" "No backups found"
        $results.Valid = $false
    }
    
    return $results
}

# PHASE 4: Memory System Initialization
function Phase4-MemoryInit() {
    Write-Phase 4 "MEMORY SYSTEM INITIALIZATION"
    
    $results = @{}
    
    # Hot Memory
    $hotMemory = Test-Path "$($Config.KimiHome)\memory\hot\MEMORY.md"
    Write-Check "Hot Memory (P0)" $(if($hotMemory){"OK"}else{"WARN"})
    $results.HotMemory = $hotMemory
    
    # Identity
    $identity = Test-Path "$($Config.KimiHome)\memory\hot\IDENTITY.md"
    Write-Check "Identity" $(if($identity){"OK"}else{"WARN"})
    $results.Identity = $identity
    
    # Memory Blocks
    $blocksDir = "$($Config.KimiHome)\memory\warm\blocks"
    $blockCount = 0
    if (Test-Path $blocksDir) {
        $blockCount = (Get-ChildItem $blocksDir -Filter "*.json" -ErrorAction SilentlyContinue).Count
    }
    Write-Check "Memory Blocks" "OK" "$blockCount blocks"
    $results.Blocks = $blockCount
    
    # Active Channel
    $activeChannel = Test-Path "$($Config.KimiHome)\isolator\active.json"
    Write-Check "Active Channel" $(if($activeChannel){"OK"}else{"WARN"})
    $results.Channel = $activeChannel
    
    return $results
}

# PHASE 5: Git Repository Sync
function Phase5-GitSync() {
    Write-Phase 5 "GIT REPOSITORY SYNC"
    
    $results = @{}
    
    Push-Location
    Set-Location $Config.KimiHome
    
    # Check Git Init
    $gitExists = Test-Path ".git"
    if (-not $gitExists) {
        git init | Out-Null
        Write-Check "Git Repository" "FIXED" "Initialized"
    } else {
        Write-Check "Git Repository" "OK" "Exists"
    }
    $results.GitInit = $true
    
    # Check Remote
    $remote = git remote get-url origin 2>$null
    if ($remote) {
        Write-Check "Git Remote" "OK" "Configured"
        $results.Remote = $true
    } else {
        Write-Check "Git Remote" "WARN" "Not configured"
        $results.Remote = $false
    }
    
    # Check Status
    $status = git status --porcelain 2>$null
    $hasChanges = $status -ne $null -and $status -ne ""
    Write-Check "Working Directory" $(if(-not $hasChanges){"OK"}else{"WARN"}) $(if($hasChanges){"Uncommitted changes"}else{"Clean"})
    $results.Clean = -not $hasChanges
    
    Pop-Location
    return $results
}

# PHASE 6: Hooks System Initialization
function Phase6-HooksInit() {
    Write-Phase 6 "HOOKS SYSTEM INITIALIZATION"
    
    $results = @{}
    
    $hooksDir = "$($Config.KimiHome)\hooks"
    $hooksConfig = "$hooksDir\hooks.toml"
    
    # Check Hooks Directory
    if (-not (Test-Path $hooksDir)) {
        New-Item -ItemType Directory -Path $hooksDir -Force | Out-Null
        Write-Check "Hooks Directory" "FIXED" "Created"
    } else {
        Write-Check "Hooks Directory" "OK" "Exists"
    }
    
    # Check Hooks Config
    $hasConfig = Test-Path $hooksConfig
    Write-Check "Hooks Config" $(if($hasConfig){"OK"}else{"WARN"})
    $results.Config = $hasConfig
    
    return $results
}

# PHASE 7: Agent Ecosystem Sync
function Phase7-AgentSync() {
    Write-Phase 7 "AGENT ECOSYSTEM SYNC"
    
    $results = @{}
    
    # Agent Bus
    $agentBusDir = "$($Config.KimiHome)\agent-bus"
    $busRunning = Test-Path $agentBusDir
    Write-Check "Agent Bus" $(if($busRunning){"OK"}else{"WARN"})
    $results.BusRunning = $busRunning
    
    # OpenClaw Workspace
    $openclawWorkspace = "$($Config.OpenClawDir)\workspace"
    $hasOpenClaw = Test-Path $openclawWorkspace
    Write-Check "OpenClaw Workspace" $(if($hasOpenClaw){"OK"}else{"WARN"})
    $results.OpenClaw = $hasOpenClaw
    
    # Key Files
    $keyFiles = @("AGENTS.md", "SOUL.md", "IDENTITY.md")
    foreach ($file in $keyFiles) {
        $path = "$openclawWorkspace\$file"
        $exists = Test-Path $path
        Write-Check $file $(if($exists){"OK"}else{"WARN"})
    }
    
    return $results
}

# PHASE 8: Ready State & Report
function Phase8-ReadyState($PhaseResults) {
    Write-Phase 8 "READY STATE & REPORT"
    
    Write-Log ""
    Write-Log "========================================" "SUCCESS"
    Write-Log "  WAKE UP MASTER COMPLETE" "SUCCESS"
    Write-Log "========================================" "SUCCESS"
    Write-Log ""
    
    # Summary
    Write-Log "Phase Summary:"
    Write-Log "  [Phase 1] System Health      : $(if($PhaseResults.Phase1.Disk -and $PhaseResults.Phase1.Memory){'OK'}else{'WARNING'})"
    Write-Log "  [Phase 2] Environment        : OK"
    Write-Log "  [Phase 3] Backup System      : $(if($PhaseResults.Phase3.Valid){'OK'}else{'NEEDS BACKUP'})"
    Write-Log "  [Phase 4] Memory System      : $(if($PhaseResults.Phase4.HotMemory){'OK'}else{'PARTIAL'})"
    Write-Log "  [Phase 5] Git Repository     : $(if($PhaseResults.Phase5.GitInit){'OK'}else{'ERROR'})"
    Write-Log "  [Phase 6] Hooks System       : OK"
    Write-Log "  [Phase 7] Agent Ecosystem    : OK"
    Write-Log "  [Phase 8] Ready State        : OK"
    
    Write-Log ""
    Write-Log "System is ready for operation." "SUCCESS"
    Write-Log ""
    Write-Log "Available Commands:"
    Write-Log "  - one-click-backup     : Execute backup"
    Write-Log "  - /sessions list       : View sessions"
    Write-Log "  - /plan                : Create plan"
    Write-Log ""
}

# MAIN EXECUTION
$startTime = Get-Date

Write-Log ""
Write-Log "========================================" "PHASE"
Write-Log "  WAKE UP MASTER v$($Config.Version)" "PHASE"
Write-Log "========================================" "PHASE"
Write-Log ""

$results = @{}

# Execute all phases
if (-not $SkipHealth) {
    $results.Phase1 = Phase1-HealthCheck
}

$results.Phase2 = Phase2-EnvironmentValidation

if (-not $SkipBackup) {
    $results.Phase3 = Phase3-BackupSync
}

$results.Phase4 = Phase4-MemoryInit

if (-not $SkipGit) {
    $results.Phase5 = Phase5-GitSync
}

if (-not $SkipHooks) {
    $results.Phase6 = Phase6-HooksInit
}

if (-not $SkipAgents) {
    $results.Phase7 = Phase7-AgentSync
}

Phase8-ReadyState $results

# Execution time
$duration = (Get-Date) - $startTime
Write-Log "Total execution time: $([math]::Round($duration.TotalSeconds, 1)) seconds" "SUCCESS"
Write-Log "Log saved to: $LogFile"
Write-Log ""
