#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Pre-Operation Backup Hook Wrapper
    在执行危险操作前自动调用备份
.DESCRIPTION
    将此脚本包装在危险操作前执行：
    hook-wrapper.ps1 -Operation "delete skill" -Command "actual-command"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$Operation,
    
    [Parameter(Mandatory=$false)]
    [string]$Command,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("light", "standard", "full")]
    [string]$Level = "standard"
)

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonScript = Join-Path $scriptPath "backup.py"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    Pre-Operation Safety Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否为危险操作
$result = & python $pythonScript check "$Operation" 2>&1
$exitCode = $LASTEXITCODE

if ($exitCode -ne 0) {
    Write-Host "[WARNING] Dangerous operation detected!" -ForegroundColor Yellow
    Write-Host "Operation: $Operation" -ForegroundColor White
    Write-Host ""
    
    # 自动创建备份
    Write-Host "Creating pre-operation snapshot..." -ForegroundColor Cyan
    & python $pythonScript create --level $Level --reason $Operation
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "[OK] Safety snapshot created" -ForegroundColor Green
        Write-Host ""
    }
}

# 如果提供了命令，执行它
if ($Command) {
    Write-Host "Executing: $Command" -ForegroundColor Cyan
    Write-Host ""
    
    Invoke-Expression $Command
    
    $cmdExitCode = $LASTEXITCODE
    
    Write-Host ""
    if ($cmdExitCode -eq 0) {
        Write-Host "[OK] Operation completed successfully" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Operation failed (Exit code: $cmdExitCode)" -ForegroundColor Red
        Write-Host ""
        Write-Host "You can restore to pre-operation state:" -ForegroundColor Yellow
        Write-Host "  python $pythonScript restore" -ForegroundColor White
    }
    
    exit $cmdExitCode
}
