#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Memory Isolator - Installation Script
.DESCRIPTION
    安装并初始化记忆隔离系统
#>

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Memory Isolator Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$IsolatorDir = "$env:USERPROFILE\.kimi\skills\memory-isolator"

# 初始化
Write-Host "[*] Initializing memory isolator..." -ForegroundColor Yellow

# 创建默认Channel
& python "$IsolatorDir\scripts\isolator.py" create default "Default isolated workspace"

# 创建启动器
$launcher = @"
@echo off
REM Memory Isolator Quick Commands

if "%1"=="create" goto create
if "%1"=="switch" goto switch
if "%1"=="checkpoint" goto checkpoint
if "%1"=="list" goto list
if "%1"=="status" goto status
if "%1"=="cleanup" goto cleanup
goto help

:create
python "%USERPROFILE%\.kimi\skills\memory-isolator\scripts\isolator.py" create %2 %3
goto end

:switch
python "%USERPROFILE%\.kimi\skills\memory-isolator\scripts\isolator.py" switch %2
goto end

:checkpoint
python "%USERPROFILE%\.kimi\skills\memory-isolator\scripts\isolator.py" checkpoint %2 %3
goto end

:list
python "%USERPROFILE%\.kimi\skills\memory-isolator\scripts\isolator.py" list %2
goto end

:status
python "%USERPROFILE%\.kimi\skills\memory-isolator\scripts\isolator.py" status
goto end

:cleanup
python "%USERPROFILE%\.kimi\skills\memory-isolator\scripts\isolator.py" cleanup %2
goto end

:help
echo Memory Isolator
echo Usage: memory-iso [create^|switch^|checkpoint^|list^|status^|cleanup] [args]
echo.
echo Examples:
echo   memory-iso create MyProject "Description"
echo   memory-iso switch MyProject
echo   memory-iso checkpoint before_update
echo   memory-iso status

:end
"@

$launcher | Out-File -FilePath "$env:USERPROFILE\.kimi\isolate.bat" -Encoding ASCII

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Commands:" -ForegroundColor Gray
Write-Host "  memory-iso create <name> [desc]  - Create channel" -ForegroundColor Gray
Write-Host "  memory-iso switch <name>         - Switch channel" -ForegroundColor Gray
Write-Host "  memory-iso checkpoint <name>     - Create checkpoint" -ForegroundColor Gray
Write-Host "  memory-iso status                - Show status" -ForegroundColor Gray
Write-Host ""
