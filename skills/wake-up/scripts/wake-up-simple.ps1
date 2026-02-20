#!/usr/bin/env pwsh
# Kbot Wake Up - System initialization (Simplified Version)
# Usage: wake-up-simple.ps1 [-Mode quick]

param(
    [ValidateSet("normal", "quick")]
    [string]$Mode = "normal"
)

$Config = @{
    Version = "1.0.0"
    KimiHome = "$env:USERPROFILE\.kimi"
    BackupRoot = "D:\kimi\SmartBackups"
}

function Log($Message, $Color = "White") {
    Write-Host $Message -ForegroundColor $Color
}

# Banner
Log ""
Log "========================================" "Cyan"
Log "  Kbot Wake Up Sequence v$($Config.Version)" "Cyan"
Log "========================================" "Cyan"
Log ""

$startTime = Get-Date

# Step 1: Health Check
Log "[Step 1/5] System Health Check..." "Yellow"
$disk = Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='C:'"
$freeGB = [math]::Round($disk.FreeSpace / 1GB, 2)
Log "  [OK] Disk: $freeGB GB available" "Green"

$os = Get-WmiObject -Class Win32_OperatingSystem
$availableGB = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
Log "  [OK] Memory: $availableGB GB available" "Green"

# Step 2: Backup Check
Log ""
Log "[Step 2/5] Backup Verification..." "Yellow"
if (Test-Path $Config.BackupRoot) {
    $latestBackup = Get-ChildItem $Config.BackupRoot -Directory -ErrorAction SilentlyContinue | 
        Sort-Object CreationTime -Descending | 
        Select-Object -First 1
    
    if ($latestBackup) {
        $age = (Get-Date) - $latestBackup.CreationTime
        $ageHours = [math]::Round($age.TotalHours, 1)
        Log "  [OK] Latest backup: $($latestBackup.Name) (${ageHours}h ago)" "Green"
        
        $size = (Get-ChildItem $latestBackup.FullName -Recurse -File -ErrorAction SilentlyContinue | 
            Measure-Object -Property Length -Sum).Sum
        $sizeMB = [math]::Round($size / 1MB, 2)
        Log "  [OK] Size: ${sizeMB}MB" "Green"
    } else {
        Log "  [!] No backups found" "Yellow"
    }
} else {
    Log "  [!] Backup directory not found" "Yellow"
}

# Step 3: Memory Check
Log ""
Log "[Step 3/5] Memory Loading..." "Yellow"
$hotMemory = Test-Path "$($Config.KimiHome)\memory\hot\MEMORY.md"
Log "  [$(if($hotMemory){'OK'}else{'!'})] Hot Memory: $(if($hotMemory){'Loaded'}else{'Not found'})" $(if($hotMemory){'Green'}else{'Yellow'})

$identity = Test-Path "$($Config.KimiHome)\memory\hot\IDENTITY.md"
Log "  [$(if($identity){'OK'}else{'!'})] Identity: $(if($identity){'Valid'}else{'Not found'})" $(if($identity){'Green'}else{'Yellow'})

$blocksDir = "$($Config.KimiHome)\memory\warm\blocks"
$blockCount = if (Test-Path $blocksDir) { (Get-ChildItem $blocksDir -Filter "*.json" -ErrorAction SilentlyContinue).Count } else { 0 }
Log "  [OK] Memory Blocks: $blockCount blocks" "Green"

# Step 4: Agent Check
Log ""
Log "[Step 4/5] Agent Synchronization..." "Yellow"
$agentBusDir = "$($Config.KimiHome)\agent-bus"
$busRunning = Test-Path $agentBusDir
Log "  [$(if($busRunning){'OK'}else{'!'})] Agent Bus: $(if($busRunning){'Running'}else{'Not initialized'})" $(if($busRunning){'Green'}else{'Yellow'})

$subscribersFile = "$agentBusDir\subscribers.json"
$agentCount = 0
if (Test-Path $subscribersFile) {
    try {
        $subscribers = Get-Content $subscribersFile | ConvertFrom-Json
        $agentCount = $subscribers.agents.Count
    } catch {}
}
Log "  [OK] Registered agents: $agentCount" "Green"

# Step 5: Ready
Log ""
Log "========================================" "Green"
Log "  SYSTEM READY" "Green"
Log "========================================" "Green"
Log ""
Log "Welcome back! (wave)" "Cyan"
Log ""

$duration = (Get-Date) - $startTime
Log "Wake up completed in $([math]::Round($duration.TotalSeconds, 1)) seconds" "Gray"
Log ""

Log "Available Commands:" "White"
Log "  wake-up-simple.ps1     - Run wake up sequence" "Gray"
Log "  one-click-backup       - Execute backup" "Gray"
Log "  /sessions list         - View sessions" "Gray"
Log ""
