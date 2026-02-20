#!/usr/bin/env pwsh
# Kbot Success Sound - High volume notification for task completion

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
        Sets system volume to maximum
    #>
    try {
        # Method 1: Windows Core Audio API via COM
        Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class AudioVolume {
    [DllImport("user32.dll")]
    public static extern IntPtr SendMessageW(IntPtr hWnd, int Msg, IntPtr wParam, IntPtr lParam);
    
    public static void SetVolume(int volume) {
        // Volume: 0-65535
        int vol = (volume * 65535) / 100;
        SendMessageW((IntPtr)0xFFFF, 0x319, (IntPtr)0x30292, (IntPtr)(vol << 16));
    }
}
"@ -ErrorAction SilentlyContinue

        if ([AudioVolume] -ne $null) {
            [AudioVolume]::SetVolume($global:AudioNotify_Volume)
        }
    }
    catch {
        # Fallback: Try alternative method
        try {
            $wsh = New-Object -ComObject WScript.Shell
            # Send volume up key multiple times
            for ($i = 0; $i -lt 50; $i++) {
                $wsh.SendKeys([char]174)  # Volume down to reset
            }
            for ($i = 0; $i -lt 50; $i++) {
                $wsh.SendKeys([char]175)  # Volume up to max
            }
        }
        catch {}
    }
}

function Play-SuccessSound {
    <#
    .SYNOPSIS
        Plays high-pitch success sound
    #>
    $freq = if ($global:AudioNotify_SuccessFrequency) { $global:AudioNotify_SuccessFrequency } else { 1000 }
    $dur = if ($global:AudioNotify_SuccessDuration) { $global:AudioNotify_SuccessDuration } else { 300 }
    $customPath = if ($global:AudioNotify_CustomSuccessPath) { $global:AudioNotify_CustomSuccessPath } else { "" }
    
    # Check for custom audio file
    if ($customPath -and (Test-Path $customPath)) {
        try {
            $player = New-Object System.Media.SoundPlayer $customPath
            $player.PlaySync()
            return
        }
        catch {
            Write-Host "[WARNING] Custom sound failed, using fallback" -ForegroundColor Yellow
        }
    }
    
    # Method 1: System Sounds
    try {
        [System.Media.SystemSounds]::Beep.Play()
    }
    catch {}
    
    # Method 2: Console Beep (high frequency, pleasant tone)
    try {
        [console]::Beep($freq, $dur)
        Start-Sleep -Milliseconds 100
        [console]::Beep($freq + 200, $dur)  # Slight pitch increase for pleasant effect
    }
    catch {
        # Method 3: Ultimate fallback - ANSI bell
        Write-Host "`a" -NoNewline
    }
}

# Main execution
try {
    # Set volume to max
    Set-MaxVolume
    
    # Play sound
    Play-SuccessSound
    
    if ($Test) {
        Write-Host "[✓] Success sound played" -ForegroundColor Green
    }
}
catch {
    Write-Host "[ERROR] Failed to play success sound: $_" -ForegroundColor Red
}
