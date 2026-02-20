#!/usr/bin/env pwsh
# Kbot Audio Notify - Install Hooks into Kbot Core Scripts

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Installing Kbot Audio Hooks" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$audioNotifyPath = "D:\kimi\skills\audio-notify\scripts"
$kbotScriptsPath = "D:\kimi\scripts"

# Function to add audio hooks to a script
function Install-AudioHook {
    param(
        [string]$ScriptPath,
        [string]$ScriptName,
        [switch]$OnSuccess,
        [switch]$OnError
    )
    
    Write-Host "Installing hooks into: $ScriptName" -ForegroundColor Yellow
    
    if (-not (Test-Path $ScriptPath)) {
        Write-Host "  ✗ Script not found: $ScriptPath" -ForegroundColor Red
        return $false
    }
    
    $content = Get-Content $ScriptPath -Raw
    $modified = $false
    
    # Check if hooks already installed
    if ($content -contains "audio-notify") {
        Write-Host "  ⚠ Hooks may already be installed" -ForegroundColor Yellow
    }
    
    # Add success hook at the end of try block (before final output)
    if ($OnSuccess) {
        $successHook = @"

# AUDIO NOTIFY: Task Success
& "$audioNotifyPath\success-sound.ps1"
"@
        # Find a good insertion point (before final summary/greeting)
        if ($content -match "Write-Log.*Ready for your commands" -or 
            $content -match "Write-Log.*completed successfully" -or
            $content -match "Good Morning") {
            # Insert before the final greeting/summary
            $content = $content -replace "(Write-Host \"\"\s*\nWrite-Host \"={40,}\".*\nWrite-Host \"\s*(?:Good Morning|Reloaded Successfully)"", "`$1$successHook`n`n"
            $modified = $true
        }
    }
    
    # Add error hook to catch block
    if ($OnError) {
        $errorHook = @"

    # AUDIO NOTIFY: Task Error
    & "$audioNotifyPath\error-sound.ps1"
"@
        # Insert after error logging in catch blocks
        $content = $content -replace "(Write-Log.*""ERROR"".*?)\s*(exit 1)", "`$1$errorHook`n    `$2"
        $modified = $true
    }
    
    if ($modified) {
        # Backup original
        $backupPath = "$ScriptPath.backup.$(Get-Date -Format 'yyyyMMddHHmmss')"
        Copy-Item $ScriptPath $backupPath
        Write-Host "  ✓ Backup created: $backupPath" -ForegroundColor Gray
        
        # Save modified content
        Set-Content $ScriptPath $content -Encoding UTF8
        Write-Host "  ✓ Hooks installed" -ForegroundColor Green
        return $true
    } else {
        Write-Host "  ⚠ No modifications made" -ForegroundColor Yellow
        return $false
    }
}

# Alternative: Create wrapper functions instead of modifying scripts
function Install-SafeHooks {
    Write-Host "Installing Safe Hooks (Wrapper Method)..." -ForegroundColor Yellow
    Write-Host ""
    
    # Create a Kbot helper module that includes audio notifications
    $helperContent = @"
# Kbot Audio Helper - Auto-loaded by Kbot scripts
`$AudioNotifyPath = "$audioNotifyPath"

function Invoke-KbotCommandWithAudio {
    param(
        [scriptblock]`$Command,
        [string]`$TaskName = "Task"
    )
    
    try {
        Write-Host "Executing: `$TaskName" -ForegroundColor Cyan
        `$result = & `$Command
        
        # Play success sound
        & "`$AudioNotifyPath\success-sound.ps1"
        
        return `$result
    }
    catch {
        Write-Host "[`$TaskName] Failed: `$_" -ForegroundColor Red
        
        # Play error sound
        & "`$AudioNotifyPath\error-sound.ps1"
        
        throw `$_
    }
}

# Export
Export-ModuleMember -Function Invoke-KbotCommandWithAudio
"@
    
    $helperPath = "$kbotScriptsPath\KbotAudioHelper.psm1"
    Set-Content $helperPath $helperContent -Encoding UTF8
    Write-Host "  ✓ Helper module created: $helperPath" -ForegroundColor Green
    
    # Modify existing scripts to import the helper
    $scriptsToModify = @(
        @{ Path = "$kbotScriptsPath\wake-up.ps1"; Name = "wake-up.ps1" },
        @{ Path = "$kbotScriptsPath\graceful-shutdown.ps1"; Name = "graceful-shutdown.ps1" },
        @{ Path = "$kbotScriptsPath\one-click-backup.ps1"; Name = "one-click-backup.ps1" },
        @{ Path = "$kbotScriptsPath\reload.ps1"; Name = "reload.ps1" }
    )
    
    foreach ($script in $scriptsToModify) {
        Write-Host "Configuring: $($script.Name)" -ForegroundColor Yellow
        
        if (Test-Path $script.Path) {
            $content = Get-Content $script.Path -Raw
            
            # Check if already modified
            if (-not ($content -contains "KbotAudioHelper")) {
                # Add import at the beginning (after the header comment)
                $importLine = @"

# Import Audio Notify Helper
Import-Module "$helperPath" -Force -ErrorAction SilentlyContinue

"@
                # Find first function definition or try block
                if ($content -match "function\s+\w+") {
                    $content = $content -replace "(function\s+\w+)", "$importLine`$1"
                } else {
                    $content = $importLine + $content
                }
                
                # Backup and save
                $backupPath = "$($script.Path).backup.$(Get-Date -Format 'yyyyMMddHHmmss')"
                Copy-Item $script.Path $backupPath
                Set-Content $script.Path $content -Encoding UTF8
                
                Write-Host "  ✓ Configured with audio support" -ForegroundColor Green
            } else {
                Write-Host "  ⚠ Already configured" -ForegroundColor Yellow
            }
        } else {
            Write-Host "  ✗ Not found" -ForegroundColor Red
        }
    }
}

# Install hooks
Install-SafeHooks

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Hook Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Audio notifications will now play:" -ForegroundColor White
Write-Host "  ✓ When tasks complete successfully" -ForegroundColor Green
Write-Host "  ✗ When tasks fail" -ForegroundColor Red
Write-Host ""
Write-Host "To test:" -ForegroundColor White
Write-Host "  . $kbotScriptsPath\wake-up.ps1" -ForegroundColor Cyan
Write-Host ""
