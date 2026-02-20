#!/usr/bin/env pwsh
# Kbot Error Sound - High volume alarm for task failures

param(
    [switch]$Test = $false
)

# Load configuration
$configPath = Join-Path $PSScriptRoot "config.ps1"
if (Test-Path $configPath) {
    . $configPath
}

function Set-MaxVolume {
    <#
    .SYNOPSIS
        Sets system volume to maximum for error alarm
    #>
    try {
        Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class AudioVolumeError {
    [DllImport("user32.dll")]
    public static extern IntPtr SendMessageW(IntPtr hWnd, int Msg, IntPtr wParam, IntPtr lParam);
    
    public static void SetVolume(int volume) {
        int vol = (volume * 65535) / 100;
        SendMessageW((IntPtr)0xFFFF, 0x319, (IntPtr)0x30292, (IntPtr)(vol << 16));
    }
}
"@ -ErrorAction SilentlyContinue

        if ([AudioVolumeError] -ne $null) {
            [AudioVolumeError]::SetVolume(100)  # Always max for errors
        }
    }
    catch {
        try {
            $wsh = New-Object -ComObject WScript.Shell
            for ($i = 0; $i -lt 50; $i++) {
                $wsh.SendKeys([char]174)
            }
            for ($i = 0; $i -lt 50; $i++) {
                $wsh.SendKeys([char]175)
            }
        }
        catch {}
    }
}

function Play-ErrorSound {
    <#
    .SYNOPSIS
        Plays loud error alarm (repeated for emphasis)
    #>
    $freq = if ($global:AudioNotify_ErrorFrequency) { $global:AudioNotify_ErrorFrequency } else { 800 }
    $dur = if ($global:AudioNotify_ErrorDuration) { $global:AudioNotify_ErrorDuration } else { 500 }
    $repeat = if ($global:AudioNotify_ErrorRepeat) { $global:AudioNotify_ErrorRepeat } else { 3 }
    $delay = if ($global:AudioNotify_ErrorDelay) { $global:AudioNotify_ErrorDelay } else { 200 }
    $customPath = if ($global:AudioNotify_CustomErrorPath) { $global:AudioNotify_CustomErrorPath } else { "" }
    
    # Check for custom audio file
    if ($customPath -and (Test-Path $customPath)) {
        try {
            for ($i = 0; $i -lt $repeat; $i++) {
                $player = New-Object System.Media.SoundPlayer $customPath
                $player.PlaySync()
                if ($i -lt $repeat - 1) {
                    Start-Sleep -Milliseconds $delay
                }
            }
            return
        }
        catch {
            Write-Host "[WARNING] Custom sound failed, using fallback" -ForegroundColor Yellow
        }
    }
    
    # Play system error sound + console beeps (multiple times for emphasis)
    for ($i = 0; $i -lt $repeat; $i++) {
        # System error sound
        try {
            [System.Media.SystemSounds]::Hand.Play()
        }
        catch {}
        
        # Console beep (low frequency for urgency)
        try {
            [console]::Beep($freq, $dur)
        }
        catch {
            Write-Host "`a" -NoNewline
        }
        
        if ($i -lt $repeat - 1) {
            Start-Sleep -Milliseconds $delay
        }
    }
}

# Main execution
try {
    # Set volume to max (errors always at max volume)
    Set-MaxVolume
    
    # Play error sound (multiple times)
    Play-ErrorSound
    
    if ($Test) {
        Write-Host "[✗] Error alarm played (3 tones)" -ForegroundColor Red
    }
}
catch {
    Write-Host "[ERROR] Failed to play error sound: $_" -ForegroundColor Red
}
