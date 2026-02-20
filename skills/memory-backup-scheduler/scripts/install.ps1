#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Memory Backup Scheduler - Installation Script
.DESCRIPTION
    安装并初始化记忆备份调度系统
#>

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Memory Backup Scheduler Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$SchedulerDir = "$env:USERPROFILE\.kimi\skills\memory-backup-scheduler"
$BackupDir = "D:\kimi\Backups"

# 检查备份目录
Write-Host "[*] Checking backup directory..." -ForegroundColor Yellow
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
    Write-Host "    Created: $BackupDir" -ForegroundColor Green
} else {
    Write-Host "    Exists: $BackupDir" -ForegroundColor Green
}

# 初始化
Write-Host "[*] Initializing scheduler..." -ForegroundColor Yellow
& python "$SchedulerDir\scripts\scheduler.py" init

# 创建启动器
$launcher = @"
@echo off
REM Memory Backup Scheduler Quick Commands

if "%1"=="init" goto init
if "%1"=="backup" goto backup
if "%1"=="push" goto push
if "%1"=="list" goto list
if "%1"=="status" goto status
goto help

:init
python "%USERPROFILE%\.kimi\skills\memory-backup-scheduler\scripts\scheduler.py" init
goto end

:backup
python "%USERPROFILE%\.kimi\skills\memory-backup-scheduler\scripts\scheduler.py" backup %2 %3
goto end

:push
python "%USERPROFILE%\.kimi\skills\memory-backup-scheduler\scripts\scheduler.py" push %2
goto end

:list
python "%USERPROFILE%\.kimi\skills\memory-backup-scheduler\scripts\scheduler.py" list %2
goto end

:status
python "%USERPROFILE%\.kimi\skills\memory-backup-scheduler\scripts\scheduler.py" status
goto end

:help
echo Memory Backup Scheduler
echo Usage: memory-backup [init^|backup^|push^|list^|status] [args]
echo.
echo Examples:
echo   memory-backup init
echo   memory-backup backup incremental P1
echo   memory-backup status

:end
"@

$launcher | Out-File -FilePath "$env:USERPROFILE\.kimi\backup.bat" -Encoding ASCII

# 创建一键备份脚本 (整合三个技能)
$oneclick = @"
@echo off
echo ========================================
echo   KbotGenesis Memory System - One-Click
echo ========================================
echo.

echo [1/3] Checking directory health...
python "%USERPROFILE%\.kimi\skills\memory-directory-manager\scripts\manager.py" health

echo.
echo [2/3] Creating checkpoint...
python "%USERPROFILE%\.kimi\skills\memory-isolator\scripts\isolator.py" checkpoint auto_backup

echo.
echo [3/3] Executing backup...
python "%USERPROFILE%\.kimi\skills\memory-backup-scheduler\scripts\scheduler.py" backup incremental P0+P1

echo.
echo ========================================
echo   Backup Complete!
echo ========================================
pause
"@

$oneclick | Out-File -FilePath "$env:USERPROFILE\.kimi\oneclick-backup.bat" -Encoding ASCII

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Commands:" -ForegroundColor Gray
Write-Host "  memory-backup init               - Initialize" -ForegroundColor Gray
Write-Host "  memory-backup backup [type] [P]  - Execute backup" -ForegroundColor Gray
Write-Host "  memory-backup status             - Show status" -ForegroundColor Gray
Write-Host "  oneclick-backup                  - One-click full backup" -ForegroundColor Gray
Write-Host ""
