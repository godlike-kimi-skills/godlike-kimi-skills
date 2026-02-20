#!/usr/bin/env pwsh
# Project Closure Verification Script
# 项目关闭验证脚本 - 确保项目彻底清理完成
# 用法: .\verify-closure.ps1 -ProjectName "WinSage"

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectName,
    
    [string]$ArchivePath = "D:\kimi\archive",
    [string]$MemoryPath = "D:\kimi\business-memory"
)

$ErrorActionPreference = "Continue"

function Write-Check($message, $status) {
    switch ($status) {
        "PASS" { Write-Host "  [✓] $message" -ForegroundColor Green }
        "FAIL" { Write-Host "  [✗] $message" -ForegroundColor Red }
        "WARN" { Write-Host "  [!] $message" -ForegroundColor Yellow }
        "INFO" { Write-Host "  [i] $message" -ForegroundColor Cyan }
    }
}

Write-Host ""
Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host "        PROJECT CLOSURE VERIFICATION" -ForegroundColor Cyan
Write-Host "        Project: $ProjectName" -ForegroundColor Cyan
Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host ""

$allPassed = $true

# 1. Check Scheduled Tasks
Write-Host "[1/6] Checking Scheduled Tasks..." -ForegroundColor Yellow
$tasks = Get-ScheduledTask -TaskName "*$ProjectName*" -ErrorAction SilentlyContinue
if ($tasks) {
    Write-Check "Found $($tasks.Count) residual task(s):" "FAIL"
    foreach ($task in $tasks) {
        Write-Check "  - $($task.TaskName) [$($task.State)]" "WARN"
    }
    $allPassed = $false
} else {
    Write-Check "No residual scheduled tasks" "PASS"
}

# 2. Check Running Processes
Write-Host ""
Write-Host "[2/6] Checking Running Processes..." -ForegroundColor Yellow
$processes = Get-Process | Where-Object { $_.ProcessName -like "*$ProjectName*" }
if ($processes) {
    Write-Check "Found $($processes.Count) running process(es)" "FAIL"
    foreach ($proc in $processes) {
        Write-Check "  - $($proc.ProcessName) (PID: $($proc.Id))" "WARN"
    }
    $allPassed = $false
} else {
    Write-Check "No residual processes" "PASS"
}

# 3. Check Services
Write-Host ""
Write-Host "[3/6] Checking Services..." -ForegroundColor Yellow
$services = Get-Service | Where-Object { $_.Name -like "*$ProjectName*" }
if ($services) {
    Write-Check "Found $($services.Count) service(s)" "FAIL"
    foreach ($svc in $services) {
        Write-Check "  - $($svc.Name) [$($svc.Status)]" "WARN"
    }
    $allPassed = $false
} else {
    Write-Check "No residual services" "PASS"
}

# 4. Check Archive
Write-Host ""
Write-Host "[4/6] Checking Archive..." -ForegroundColor Yellow
$archived = Get-ChildItem $ArchivePath -Directory -Filter "*$ProjectName*" -ErrorAction SilentlyContinue
if ($archived) {
    Write-Check "Files archived: $($archived[0].FullName)" "PASS"
} else {
    Write-Check "No archive folder found" "WARN"
}

# 5. Check Postmortem Documents
Write-Host ""
Write-Host "[5/6] Checking Postmortem Documents..." -ForegroundColor Yellow
$postmortem = Get-ChildItem $MemoryPath -File -Filter "postmortem-*$ProjectName*" -ErrorAction SilentlyContinue
$lessons = Get-ChildItem $MemoryPath -File -Filter "lessons-learned-*$ProjectName*" -ErrorAction SilentlyContinue

if ($postmortem) {
    Write-Check "Postmortem document exists" "PASS"
} else {
    Write-Check "Postmortem document NOT found" "FAIL"
    $allPassed = $false
}

if ($lessons) {
    Write-Check "Lessons learned document exists" "PASS"
} else {
    Write-Check "Lessons learned document NOT found" "WARN"
}

# 6. Check Active Directories
Write-Host ""
Write-Host "[6/6] Checking Active Project Directories..." -ForegroundColor Yellow
$activeDirs = @(
    "D:\kimi\$ProjectName",
    "D:\kimi\projects\$ProjectName"
)

$foundActive = $false
foreach ($dir in $activeDirs) {
    if (Test-Path $dir) {
        Write-Check "Active directory exists: $dir" "WARN"
        $foundActive = $true
    }
}

if (-not $foundActive) {
    Write-Check "No active project directories" "PASS"
}

# Summary
Write-Host ""
Write-Host "===============================================================" -ForegroundColor Cyan

if ($allPassed) {
    Write-Host "  ✓ VERIFICATION PASSED" -ForegroundColor Green
    Write-Host "  Project '$ProjectName' is properly closed." -ForegroundColor Green
    exit 0
} else {
    Write-Host "  ✗ VERIFICATION FAILED" -ForegroundColor Red
    Write-Host "  Project '$ProjectName' has residual items." -ForegroundColor Red
    Write-Host "  Please review FAIL items above and clean up." -ForegroundColor Yellow
    exit 1
}
