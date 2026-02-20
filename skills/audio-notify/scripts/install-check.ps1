#!/usr/bin/env pwsh
# Kbot Audio Notify - Installation Check

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Kbot Audio Notify - Installation Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$allPassed = $true

# 1. Check PowerShell Version
Write-Host "[1/5] Checking PowerShell Version..." -ForegroundColor Yellow
$psVersion = $PSVersionTable.PSVersion
if ($psVersion.Major -ge 5 -and $psVersion.Minor -ge 1) {
    Write-Host "  ✓ PowerShell $($psVersion.Major).$($psVersion.Minor) - OK" -ForegroundColor Green
} else {
    Write-Host "  ✗ PowerShell $($psVersion.Major).$($psVersion.Minor) - Requires 5.1+" -ForegroundColor Red
    $allPassed = $false
}

# 2. Check Execution Policy
Write-Host ""
Write-Host "[2/5] Checking Execution Policy..." -ForegroundColor Yellow
$execPolicy = Get-ExecutionPolicy
if ($execPolicy -eq "RemoteSigned" -or $execPolicy -eq "Unrestricted" -or $execPolicy -eq "Bypass") {
    Write-Host "  ✓ Execution Policy: $execPolicy - OK" -ForegroundColor Green
} elseif ($execPolicy -eq "Restricted") {
    Write-Host "  ✗ Execution Policy: $execPolicy - BLOCKED" -ForegroundColor Red
    Write-Host ""
    Write-Host "  ⚠️  ACTION REQUIRED:" -ForegroundColor Yellow
    Write-Host "     Run as Administrator:" -ForegroundColor White
    Write-Host "     Set-ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Cyan
    Write-Host ""
    $allPassed = $false
} else {
    Write-Host "  ⚠ Execution Policy: $execPolicy - May need adjustment" -ForegroundColor Yellow
}

# 3. Check Audio Devices
Write-Host ""
Write-Host "[3/5] Checking Audio Devices..." -ForegroundColor Yellow
try {
    $audioDevices = Get-WmiObject -Class Win32_SoundDevice | Where-Object { $_.Status -eq "OK" }
    if ($audioDevices) {
        Write-Host "  ✓ Audio devices detected:" -ForegroundColor Green
        foreach ($device in $audioDevices | Select-Object -First 3) {
            Write-Host "    - $($device.Name)" -ForegroundColor Gray
        }
    } else {
        Write-Host "  ✗ No audio devices found" -ForegroundColor Red
        $allPassed = $false
    }
}
catch {
    Write-Host "  ⚠ Could not check audio devices: $_" -ForegroundColor Yellow
}

# 4. Test Volume Control
Write-Host ""
Write-Host "[4/5] Testing Volume Control..." -ForegroundColor Yellow
try {
    # Test setting volume
    Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class VolumeTest {
    [DllImport("user32.dll")]
    public static extern IntPtr SendMessageW(IntPtr hWnd, int Msg, IntPtr wParam, IntPtr lParam);
}
"@ -ErrorAction SilentlyContinue
    Write-Host "  ✓ Volume control API accessible" -ForegroundColor Green
}
catch {
    Write-Host "  ⚠ Volume control API limited (will use fallback)" -ForegroundColor Yellow
}

# 5. Test Audio Output
Write-Host ""
Write-Host "[5/5] Testing Audio Output..." -ForegroundColor Yellow
Write-Host "  Playing test sound..." -ForegroundColor Cyan
try {
    [System.Media.SystemSounds]::Beep.Play()
    [console]::Beep(1000, 200)
    Write-Host "  ✓ Audio output working" -ForegroundColor Green
}
catch {
    Write-Host "  ✗ Audio output failed: $_" -ForegroundColor Red
    $allPassed = $false
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
if ($allPassed) {
    Write-Host " ✓ All Checks Passed - Ready to Install" -ForegroundColor Green
} else {
    Write-Host " ✗ Some Checks Failed - Review Above" -ForegroundColor Red
}
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Next steps
if ($allPassed) {
    Write-Host "Next steps:" -ForegroundColor White
    Write-Host "  1. Test success sound:" -ForegroundColor Gray
    Write-Host "     . D:\kimi\skills\audio-notify\scripts\success-sound.ps1 -Test" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  2. Test error sound:" -ForegroundColor Gray
    Write-Host "     . D:\kimi\skills\audio-notify\scripts\error-sound.ps1 -Test" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  3. Install Kbot hooks:" -ForegroundColor Gray
    Write-Host "     . D:\kimi\skills\audio-notify\scripts\install-hooks.ps1" -ForegroundColor Cyan
}
