#!/usr/bin/env pwsh
# Kbot Audio Notify - Uninstall Script

Write-Host ""
Write-Host "========================================" -ForegroundColor Red
Write-Host " Uninstall Kbot Audio Notify" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""

Write-Host "This will remove:" -ForegroundColor Yellow
Write-Host "  - Audio notify skill files" -ForegroundColor Gray
Write-Host "  - Kbot hooks and helper module" -ForegroundColor Gray
Write-Host "  - Configuration files" -ForegroundColor Gray
Write-Host ""

$confirm = Read-Host "Are you sure? (yes/no)"
if ($confirm -ne "yes") {
    Write-Host "Uninstall cancelled." -ForegroundColor Yellow
    exit 0
}

$removed = @()
$errors = @()

# 1. Remove hooks from Kbot scripts
Write-Host ""
Write-Host "[1/4] Removing hooks from Kbot scripts..." -ForegroundColor Yellow

$scriptsToClean = @(
    "D:\kimi\scripts\wake-up.ps1",
    "D:\kimi\scripts\graceful-shutdown.ps1",
    "D:\kimi\scripts\one-click-backup.ps1",
    "D:\kimi\scripts\reload.ps1"
)

foreach ($scriptPath in $scriptsToClean) {
    if (Test-Path $scriptPath) {
        $content = Get-Content $scriptPath -Raw
        $originalContent = $content
        
        # Remove audio-notify references
        $content = $content -replace "# AUDIO NOTIFY:.*?\n", ""
        $content = $content -replace "& \".*?audio-notify.*?\".*?\n", ""
        $content = $content -replace "# Import Audio Notify Helper.*?\n", ""
        $content = $content -replace "Import-Module \".*?KbotAudioHelper.*?\".*?\n", ""
        
        if ($content -ne $originalContent) {
            Set-Content $scriptPath $content -Encoding UTF8
            Write-Host "  ✓ Cleaned: $(Split-Path $scriptPath -Leaf)" -ForegroundColor Green
            $removed += "Hook from $(Split-Path $scriptPath -Leaf)"
        }
    }
}

# 2. Remove helper module
Write-Host ""
Write-Host "[2/4] Removing helper module..." -ForegroundColor Yellow
$helperPath = "D:\kimi\scripts\KbotAudioHelper.psm1"
if (Test-Path $helperPath) {
    Remove-Item $helperPath -Force
    Write-Host "  ✓ Removed: KbotAudioHelper.psm1" -ForegroundColor Green
    $removed += "Helper module"
} else {
    Write-Host "  ⚠ Helper module not found" -ForegroundColor Yellow
}

# 3. Remove audio notify skill directory
Write-Host ""
Write-Host "[3/4] Removing skill files..." -ForegroundColor Yellow
$skillPath = "D:\kimi\skills\audio-notify"
if (Test-Path $skillPath) {
    Remove-Item $skillPath -Recurse -Force
    Write-Host "  ✓ Removed: audio-notify skill directory" -ForegroundColor Green
    $removed += "Skill directory"
} else {
    Write-Host "  ⚠ Skill directory not found" -ForegroundColor Yellow
}

# 4. Restore backups if any
Write-Host ""
Write-Host "[4/4] Checking for backups to restore..." -ForegroundColor Yellow
$backups = Get-ChildItem "D:\kimi\scripts\*.backup.*" -ErrorAction SilentlyContinue
if ($backups) {
    Write-Host "  Found $($backups.Count) backup(s):" -ForegroundColor Yellow
    foreach ($backup in $backups) {
        Write-Host "    - $($backup.Name)" -ForegroundColor Gray
    }
    Write-Host ""
    Write-Host "  Backups preserved for manual restoration." -ForegroundColor Cyan
    Write-Host "  To restore a backup, manually rename it (remove .backup.* extension)." -ForegroundColor Gray
} else {
    Write-Host "  No backups found" -ForegroundColor Gray
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Red
Write-Host " Uninstall Complete" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""

if ($removed.Count -gt 0) {
    Write-Host "Removed items:" -ForegroundColor White
    foreach ($item in $removed) {
        Write-Host "  ✓ $item" -ForegroundColor Green
    }
} else {
    Write-Host "Nothing was removed (already uninstalled?)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Kbot Audio Notify has been uninstalled." -ForegroundColor White
Write-Host "Your Kbot scripts will no longer play audio notifications." -ForegroundColor Gray
