#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Wake Up Master (Quick Mode) - Essential 5-Step Wake Up
.DESCRIPTION
    Quick wake-up for daily use - only essential phases.
    Skips: Security scan, Skills update check, Agent Bus sync
    
    Phases:
    1. System Health Check
    2. Environment Validation
    3. Backup System Sync
    4. Memory System Initialization
    5. Ready State
#>

# Configuration
$KimiHome = "$env:USERPROFILE\.kimi"
$BackupRoot = "D:\kimi\SmartBackups"
$Version = "2.0.0-quick"
$StartTime = Get-Date
$LastStartFile = "$KimiHome\memory\hot\last-wake-up.json"

# Read last start time
$Uptime = $null
if (Test-Path $LastStartFile) {
    try {
        $LastStartInfo = Get-Content $LastStartFile | ConvertFrom-Json
        $lastStart = [DateTime]::Parse($LastStartInfo.StartTime)
        $Uptime = $StartTime - $lastStart
    } catch {}
}

# Utility Functions
function Write-Step($Num, $Total, $Message) {
    Write-Host ""
    Write-Host "[Step $Num/$Total] $Message..." -ForegroundColor Cyan
}

function Write-Check($Item, $Status, $Details = "") {
    $icon = switch ($Status) {
        "OK"   { "[OK]" }
        "WARN" { "[!]" }
        "FAIL" { "[X]" }
        "NEW"  { "[+]" }
        default { "[ ]" }
    }
    $color = switch ($Status) {
        "OK"   { "Green" }
        "WARN" { "Yellow" }
        "FAIL" { "Red" }
        "NEW"  { "Cyan" }
        default { "White" }
    }
    
    if ($Details) {
        Write-Host "  $icon $Item : $Details" -ForegroundColor $color
    } else {
        Write-Host "  $icon $Item" -ForegroundColor $color
    }
}

# Header
Write-Host ""
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "    WAKE UP MASTER v$Version" -ForegroundColor Cyan
Write-Host "    Quick Mode - 5 Essential Phases" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan

# Step 1: Health Check
function Step1-Health() {
    Write-Step 1 5 "SYSTEM HEALTH CHECK"
    
    try {
        $disk = Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='C:'" -ErrorAction Stop
        $freeGB = [math]::Round($disk.FreeSpace / 1GB, 2)
        Write-Check "Disk" "OK" "$freeGB GB free"
    } catch {
        Write-Check "Disk" "FAIL" "Cannot read"
    }
    
    try {
        $os = Get-WmiObject -Class Win32_OperatingSystem -ErrorAction Stop
        $availGB = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
        Write-Check "Memory" "OK" "$availGB GB free"
    } catch {
        Write-Check "Memory" "FAIL" "Cannot read"
    }
    
    $net = Test-Connection -ComputerName "8.8.8.8" -Count 1 -Quiet
    Write-Check "Network" $(if($net){"OK"}else{"WARN"}) $(if($net){"Connected"}else{"Offline"})
}

# Step 2: Environment
function Step2-Environment() {
    Write-Step 2 5 "ENVIRONMENT VALIDATION"
    
    $configExists = Test-Path "$KimiHome\config.toml"
    Write-Check "Config" $(if($configExists){"OK"}else{"WARN"})
    
    $essentialDirs = @("skills", "scripts", "memory")
    $allExist = $true
    foreach ($dir in $essentialDirs) {
        if (-not (Test-Path "$KimiHome\$dir")) { $allExist = $false }
    }
    Write-Check "Directories" $(if($allExist){"OK"}else{"WARN"})
    
    $gitExists = $null -ne (Get-Command git -ErrorAction SilentlyContinue)
    Write-Check "Git" $(if($gitExists){"OK"}else{"WARN"})
}

# Step 3: Backup
function Step3-Backup() {
    Write-Step 3 5 "BACKUP VERIFICATION"
    
    if (-not (Test-Path $BackupRoot)) {
        Write-Check "Backup Dir" "WARN" "Not found"
        return
    }
    
    $latest = Get-ChildItem $BackupRoot -Directory | 
        Sort-Object CreationTime -Descending | 
        Select-Object -First 1
    
    if ($latest) {
        $age = (Get-Date) - $latest.CreationTime
        $hours = [math]::Round($age.TotalHours, 1)
        $recent = $hours -lt 24
        
        $size = (Get-ChildItem $latest.FullName -Recurse -File | 
            Measure-Object -Property Length -Sum).Sum
        $sizeMB = [math]::Round($size / 1MB, 2)
        
        Write-Check "Latest Backup" $(if($recent){"OK"}else{"WARN"}) "${hours}h ago, ${sizeMB} MB"
    } else {
        Write-Check "Backups" "WARN" "None found"
    }
}

# Step 4: Memory
function Step4-Memory() {
    Write-Step 4 5 "MEMORY LOADING"
    
    $hot = Test-Path "$KimiHome\memory\hot\MEMORY.md"
    Write-Check "Hot Memory" $(if($hot){"OK"}else{"WARN"})
    
    $id = Test-Path "$KimiHome\memory\hot\IDENTITY.md"
    Write-Check "Identity" $(if($id){"OK"}else{"WARN"})
    
    $blocksDir = "$KimiHome\memory\warm\blocks"
    $count = if(Test-Path $blocksDir) { 
        (Get-ChildItem $blocksDir -Filter "*.json" -ErrorAction SilentlyContinue).Count 
    } else { 0 }
    Write-Check "Memory Blocks" "OK" "$count loaded"
    
    $channel = Test-Path "$KimiHome\isolator\active.json"
    Write-Check "Active Channel" $(if($channel){"OK"}else{"WARN"})
}

# Step 5: Ready
function Step5-Ready() {
    Write-Step 5 5 "READY STATE"
    
    # Skills count
    $skillsDir = "$KimiHome\skills"
    $skillCount = if(Test-Path $skillsDir) { 
        (Get-ChildItem $skillsDir -Directory -ErrorAction SilentlyContinue).Count 
    } else { 0 }
    
    Write-Host ""
    Write-Host "===========================================" -ForegroundColor Green
    Write-Host "         SYSTEM READY" -ForegroundColor Green
    Write-Host "===========================================" -ForegroundColor Green
    Write-Host ""
    
    # Uptime Report
    if ($script:Uptime) {
        $days = $script:Uptime.Days
        $hours = $script:Uptime.Hours
        $minutes = $script:Uptime.Minutes
        $seconds = $script:Uptime.Seconds
        
        $uptimeString = ""
        if ($days -gt 0) { $uptimeString += "$days days " }
        if ($hours -gt 0) { $uptimeString += "$hours hours " }
        if ($minutes -gt 0) { $uptimeString += "$minutes minutes " }
        if ($uptimeString -eq "" -and $seconds -gt 0) { $uptimeString = "$seconds seconds" }
        if ($uptimeString -eq "") { $uptimeString = "less than 1 second" }
        
        Write-Host "UPTIME REPORT:" -ForegroundColor Cyan
        Write-Host "  System ran for: $uptimeString"
        Write-Host ""
    }
    
    Write-Host "Status Summary:"
    Write-Host "  - Skills Available: $skillCount"
    Write-Host "  - Quick Mode: Active (5/13 phases)"
    Write-Host ""
    Write-Host "For full wake up with all features:"
    Write-Host "  wake up              # Full 13-phase mode"
    Write-Host "  wake up --security   # Include security scan"
    Write-Host "  wake up --tasks      # Include task report"
    Write-Host ""
    Write-Host "Quick Commands:"
    Write-Host "  one-click-backup     - Run backup"
    Write-Host "  /sessions list       - View sessions"
    Write-Host "  /plan                - Create plan"
    Write-Host ""
}

# Execute
Step1-Health
Step2-Environment
Step3-Backup
Step4-Memory
Step5-Ready

# Save current start time for next run
$duration = (Get-Date) - $StartTime
$currentStartInfo = @{
    StartTime = $StartTime.ToString("o")
    Version = $Version
    Mode = "quick"
    ExecutionSeconds = [math]::Round($duration.TotalSeconds, 1)
} | ConvertTo-Json

# Ensure directory exists
$lastStartDir = Split-Path $LastStartFile -Parent
if (-not (Test-Path $lastStartDir)) {
    New-Item -ItemType Directory -Path $lastStartDir -Force | Out-Null
}

$currentStartInfo | Out-File -FilePath $LastStartFile -Force
Write-Host "Start time saved for next wake up" -ForegroundColor Gray
