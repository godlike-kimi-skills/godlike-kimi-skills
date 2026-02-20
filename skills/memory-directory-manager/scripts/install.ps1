#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Memory Directory Manager - Installation Script
.DESCRIPTION
    安装并初始化三层记忆架构
#>

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Memory Directory Manager Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ManagerDir = "$env:USERPROFILE\.kimi\skills\memory-directory-manager"
$MemoryDir = "$env:USERPROFILE\.kimi\memory"

# 检查Python
Write-Host "[*] Checking Python..." -ForegroundColor Yellow
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "[!] Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}
Write-Host "    OK: Python found" -ForegroundColor Green

# 初始化架构
Write-Host "[*] Initializing memory architecture..." -ForegroundColor Yellow
& python "$ManagerDir\scripts\manager.py" init

# 创建启动器
Write-Host "[*] Creating launchers..." -ForegroundColor Yellow
$launcher = @"
@echo off
REM Memory Directory Manager Quick Commands

if "%1"=="init" goto init
if "%1"=="health" goto health
if "%1"=="archive" goto archive
if "%1"=="index" goto index
goto help

:init
python "%USERPROFILE%\.kimi\skills\memory-directory-manager\scripts\manager.py" init
goto end

:health
python "%USERPROFILE%\.kimi\skills\memory-directory-manager\scripts\manager.py" health
goto end

:archive
python "%USERPROFILE%\.kimi\skills\memory-directory-manager\scripts\manager.py" archive --dry-run
goto end

:index
python "%USERPROFILE%\.kimi\skills\memory-directory-manager\scripts\manager.py" index
goto end

:help
echo Memory Directory Manager
echo Usage: memory-dir [init^|health^|archive^|index]

:end
"@

$launcher | Out-File -FilePath "$env:USERPROFILE\.kimi\memory.bat" -Encoding ASCII

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Commands:" -ForegroundColor Gray
Write-Host "  memory-dir init    - Initialize architecture" -ForegroundColor Gray
Write-Host "  memory-dir health  - Check health" -ForegroundColor Gray
Write-Host "  memory-dir archive - Archive expired content" -ForegroundColor Gray
Write-Host "  memory-dir index   - Update index" -ForegroundColor Gray
Write-Host ""
