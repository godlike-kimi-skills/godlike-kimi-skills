#!/usr/bin/env pwsh
# Kbot Audio Notify - Test Suite

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Kbot Audio Notify - Test Suite" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Success Sound
Write-Host "[Test 1/3] Testing SUCCESS Sound..." -ForegroundColor Yellow
Write-Host "  You should hear a high-pitch pleasant tone" -ForegroundColor Gray
try {
    & "D:\kimi\skills\audio-notify\scripts\success-sound.ps1" -Test
    Start-Sleep -Seconds 1
}
catch {
    Write-Host "  X Failed: $_" -ForegroundColor Red
}

# Test 2: Error Sound
Write-Host ""
Write-Host "[Test 2/3] Testing ERROR Sound..." -ForegroundColor Red
Write-Host "  You should hear 3 loud urgent tones" -ForegroundColor Gray
try {
    & "D:\kimi\skills\audio-notify\scripts\error-sound.ps1" -Test
    Start-Sleep -Seconds 1
}
catch {
    Write-Host "  X Failed: $_" -ForegroundColor Red
}

# Test 3: Volume Control + Simulated Task
Write-Host ""
Write-Host "[Test 3/3] Testing Volume + Simulated Task..." -ForegroundColor Yellow
try {
    Write-Host "  Setting volume to maximum..." -ForegroundColor Gray
    Add-Type -TypeDefinition @"
using System; using System.Runtime.InteropServices;
public class VolumeTestFinal {
    [DllImport("user32.dll")]
    public static extern IntPtr SendMessageW(IntPtr hWnd, int Msg, IntPtr wParam, IntPtr lParam);
    public static void SetVolume(int volume) {
        int vol = (volume * 65535) / 100;
        SendMessageW((IntPtr)0xFFFF, 0x319, (IntPtr)0x30292, (IntPtr)(vol << 16));
    }
}
"@ -ErrorAction SilentlyContinue
    
    [VolumeTestFinal]::SetVolume(100)
    Write-Host "  Volume set to max, playing task completion sound..." -ForegroundColor Gray
    Start-Sleep -Milliseconds 500
    & "D:\kimi\skills\audio-notify\scripts\success-sound.ps1"
}
catch {
    Write-Host "  Warning: Volume control limited" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Test Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "If you heard all sounds, Audio Notify is working!" -ForegroundColor White
