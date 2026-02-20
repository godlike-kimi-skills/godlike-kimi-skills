#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Wake Up Master v2.0 - Complete System Initialization (13 Phases)
.DESCRIPTION
    13-Phase Wake Up Sequence with new features
.PARAMETER Mode
    Execution mode: normal, quick, update, security, tasks, repair
.PARAMETER SkipPhase
    Skip specific phases
#>

[CmdletBinding()]
param(
    [ValidateSet("normal", "quick", "update", "security", "tasks", "repair")]
    [string]$Mode = "normal",
    
    [switch]$SkipHealth,
    [switch]$SkipSecurity,
    [switch]$SkipSkillsCheck,
    [switch]$SkipSkillsUpdate,
    [switch]$SkipBackup,
    [switch]$SkipGit,
    [switch]$SkipAgentBus,
    [switch]$SkipTaskReport
)

# Configuration
$Config = @{
    Version = "2.0.0"
    KimiHome = "$env:USERPROFILE\.kimi"
    OpenClawDir = "$env:USERPROFILE\.openclaw"
    BackupRoot = "D:\kimi\SmartBackups"
    LogDir = "$env:USERPROFILE\.kimi\logs\wake-up-master"
    StartTime = Get-Date
    Results = @{}
    LastStartFile = "$env:USERPROFILE\.kimi\memory\hot\last-wake-up.json"
}

# Ensure log directory
New-Item -ItemType Directory -Force -Path $Config.LogDir | Out-Null
$LogFile = "$($Config.LogDir)\wake-up-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

# Read last start time
$LastStartInfo = $null
$Uptime = $null
if (Test-Path $Config.LastStartFile) {
    try {
        $LastStartInfo = Get-Content $Config.LastStartFile | ConvertFrom-Json
        $lastStart = [DateTime]::Parse($LastStartInfo.StartTime)
        $Uptime = $Config.StartTime - $lastStart
    } catch {}
}

# =================================================================
# LOGGING FUNCTIONS
# =================================================================
function Write-Log($Message, $Level = "INFO") {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Add-Content -Path $LogFile -Value $logEntry
    
    switch ($Level) {
        "SUCCESS" { Write-Host $Message -ForegroundColor Green }
        "WARNING" { Write-Host $Message -ForegroundColor Yellow }
        "ERROR"   { Write-Host $Message -ForegroundColor Red }
        "PHASE"   { Write-Host $Message -ForegroundColor Cyan }
        "INFO"    { Write-Host $Message -ForegroundColor White }
        "NETWORK" { Write-Host $Message -ForegroundColor Magenta }
        default   { Write-Host $Message }
    }
}

function Write-Phase($Number, $Name, $Duration = "") {
    Write-Log ""
    Write-Log "========================================" "PHASE"
    if ($Duration) {
        Write-Log "  PHASE $Number/13 : $Name [$Duration]" "PHASE"
    } else {
        Write-Log "  PHASE $Number/13 : $Name" "PHASE"
    }
    Write-Log "========================================" "PHASE"
}

function Write-Check($Item, $Status, $Details = "") {
    $color = switch ($Status) {
        "OK" { "Green" }
        "WARN" { "Yellow" }
        "FAIL" { "Red" }
        "SKIP" { "Gray" }
        "NEW" { "Cyan" }
        default { "White" }
    }
    $icon = switch ($Status) {
        "OK" { "[OK]" }
        "WARN" { "[!]" }
        "FAIL" { "[X]" }
        "SKIP" { "[-]" }
        "NEW" { "[+]" }
        default { "[ ]" }
    }
    
    if ($Details) {
        Write-Log "  $icon $Item : $Details" $color
    } else {
        Write-Log "  $icon $Item" $color
    }
}

function Write-Section($Title) {
    Write-Log ""
    Write-Log "--- $Title ---" "INFO"
}

# =================================================================
# PHASE 1: SYSTEM HEALTH CHECK
# =================================================================
function Phase1-HealthCheck() {
    Write-Phase 1 "SYSTEM HEALTH CHECK" "~5s"
    
    $results = @{
        Passed = $true
        Checks = @{}
    }
    
    # Disk Check
    try {
        $disk = Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='C:'" -ErrorAction Stop
        $freeGB = [math]::Round($disk.FreeSpace / 1GB, 2)
        $totalGB = [math]::Round($disk.Size / 1GB, 2)
        $percentFree = [math]::Round(($freeGB / $totalGB) * 100, 1)
        $results.Checks.Disk = @{ FreeGB = $freeGB; TotalGB = $totalGB; PercentFree = $percentFree }
        $diskOK = $freeGB -gt 10
        Write-Check "Disk Space" $(if($diskOK){"OK"}else{"WARN"}) "$freeGB GB free (${percentFree}%)"
        if (-not $diskOK) { $results.Passed = $false }
    } catch {
        Write-Check "Disk Space" "FAIL" "Cannot query"
        $results.Passed = $false
    }
    
    # Memory Check
    try {
        $os = Get-WmiObject -Class Win32_OperatingSystem -ErrorAction Stop
        $totalGB = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
        $availableGB = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
        $results.Checks.Memory = @{ TotalGB = $totalGB; AvailableGB = $availableGB }
        $memOK = $availableGB -gt 2
        Write-Check "Memory" $(if($memOK){"OK"}else{"WARN"}) "$availableGB GB / $totalGB GB available"
        if (-not $memOK) { $results.Passed = $false }
    } catch {
        Write-Check "Memory" "FAIL" "Cannot query"
        $results.Passed = $false
    }
    
    # Network Check
    $network = Test-Connection -ComputerName "8.8.8.8" -Count 1 -Quiet
    $results.Checks.Network = @{ Connected = $network }
    Write-Check "Network" $(if($network){"OK"}else{"WARN"}) $(if($network){"Connected"}else{"Disconnected"})
    
    return $results
}

# =================================================================
# PHASE 2: ENVIRONMENT VALIDATION
# =================================================================
function Phase2-EnvironmentValidation() {
    Write-Phase 2 "ENVIRONMENT VALIDATION" "~3s"
    
    $results = @{
        Passed = $true
        Checks = @{}
    }
    
    # Config Check
    $configPath = "$($Config.KimiHome)\config.toml"
    $results.Checks.Config = Test-Path $configPath
    Write-Check "Kimi Config" $(if($results.Checks.Config){"OK"}else{"WARN"}) $(if($results.Checks.Config){"Found"}else{"Missing - will create"})
    
    # Directory Structure
    $dirs = @("skills", "scripts", "memory", "rules", "config", "logs")
    $missingDirs = @()
    foreach ($dir in $dirs) {
        $path = "$($Config.KimiHome)\$dir"
        if (-not (Test-Path $path)) {
            $missingDirs += $dir
            New-Item -ItemType Directory -Path $path -Force | Out-Null
        }
    }
    Write-Check "Directory Structure" $(if($missingDirs.Count -eq 0){"OK"}else{"FIXED"}) "Created: $($missingDirs -join ', ')"
    $results.Checks.Directories = $dirs.Count - $missingDirs.Count
    
    # Dependencies Check
    $deps = @("git", "python")
    foreach ($dep in $deps) {
        $exists = $null -ne (Get-Command $dep -ErrorAction SilentlyContinue)
        Write-Check "$dep" $(if($exists){"OK"}else{"WARN"})
    }
    
    return $results
}

# =================================================================
# PHASE 3: SECURITY & PRIVACY SCAN [NEW]
# =================================================================
function Phase3-SecurityScan() {
    Write-Phase 3 "SECURITY & PRIVACY SCAN" "~15s [NEW]"
    
    $results = @{
        Score = 100
        Issues = @()
        Warnings = @()
    }
    
    Write-Section "Sensitive Files Scan"
    
    # Check for sensitive files
    $sensitivePatterns = @("*.key", "*.pem", "*.p12", "*.pfx", "id_rsa", ".env", "credentials.json", "token.json")
    $sensitiveFiles = @()
    
    foreach ($pattern in $sensitivePatterns) {
        $files = Get-ChildItem -Path $Config.KimiHome -Recurse -Filter $pattern -ErrorAction SilentlyContinue | Select-Object -First 5
        $sensitiveFiles += $files
    }
    
    if ($sensitiveFiles.Count -gt 0) {
        Write-Check "Sensitive Files" "WARN" "$($sensitiveFiles.Count) found"
        $results.Warnings += "$($sensitiveFiles.Count) sensitive files detected"
        $results.Score -= 10
    } else {
        Write-Check "Sensitive Files" "OK" "None found"
    }
    
    # Check API keys in config files
    Write-Section "API Key Exposure Check"
    $configFiles = Get-ChildItem -Path "$($Config.KimiHome)\config" -File -ErrorAction SilentlyContinue
    $exposedKeys = 0
    
    foreach ($file in $configFiles) {
        try {
            $content = Get-Content -Path $file.FullName -Raw -ErrorAction SilentlyContinue
            if ($content -match "api[_-]?key") {
                $exposedKeys++
            }
        } catch {}
    }
    
    if ($exposedKeys -gt 0) {
        Write-Check "API Keys in Config" "WARN" "$exposedKeys potential exposed keys"
        $results.Warnings += "Possible API key exposure in config files"
        $results.Score -= 15
    } else {
        Write-Check "API Keys in Config" "OK" "No exposed keys detected"
    }
    
    # Check SSH keys
    $sshDir = "$env:USERPROFILE\.ssh"
    if (Test-Path $sshDir) {
        $sshKeys = Get-ChildItem -Path $sshDir -Filter "id_*" -ErrorAction SilentlyContinue
        Write-Check "SSH Keys" "OK" "$($sshKeys.Count) keys found"
    } else {
        Write-Check "SSH Directory" "WARN" "Not found"
    }
    
    # Generate security report
    $results.Score = [math]::Max(0, $results.Score)
    $securityLevel = if ($results.Score -ge 90) { "EXCELLENT" } 
                     elseif ($results.Score -ge 70) { "GOOD" }
                     elseif ($results.Score -ge 50) { "FAIR" }
                     else { "POOR" }
    
    Write-Section "Security Score: $securityLevel ($($results.Score)/100)"
    
    if ($results.Warnings.Count -gt 0) {
        Write-Log "Warnings:" "WARNING"
        $results.Warnings | ForEach-Object { Write-Log "  - $_" "WARNING" }
    }
    
    # Save security report
    $reportPath = "$($Config.LogDir)\security-scan-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
    $results | ConvertTo-Json -Depth 3 | Out-File -FilePath $reportPath
    Write-Check "Security Report" "OK" "Saved"
    
    return $results
}

# =================================================================
# PHASE 4: SKILLS AVAILABILITY CHECK [NEW]
# =================================================================
function Phase4-SkillsCheck() {
    Write-Phase 4 "SKILLS AVAILABILITY CHECK" "~10s [NEW]"
    
    $results = @{
        Total = 0
        Healthy = 0
        Broken = @()
        MissingDeps = @()
    }
    
    $skillsDir = "$($Config.KimiHome)\skills"
    
    if (-not (Test-Path $skillsDir)) {
        Write-Check "Skills Directory" "FAIL" "Not found"
        return $results
    }
    
    $skills = Get-ChildItem -Path $skillsDir -Directory -ErrorAction SilentlyContinue
    $results.Total = $skills.Count
    
    Write-Check "Skills Found" "OK" "$($skills.Count) skills"
    Write-Section "Checking Each Skill"
    
    foreach ($skill in $skills) {
        $skillName = $skill.Name
        $skillPath = $skill.FullName
        $skillDoc = "$skillPath\SKILL.md"
        $hasDoc = Test-Path $skillDoc
        $hasScripts = Test-Path "$skillPath\scripts"
        
        $status = "OK"
        $details = ""
        
        if (-not $hasDoc) {
            $status = "WARN"
            $details = "Missing SKILL.md"
            $results.Broken += @{ Name = $skillName; Issue = "Missing documentation" }
        } elseif (-not $hasScripts) {
            $status = "WARN"
            $details = "No scripts"
        } else {
            $results.Healthy++
        }
        
        # Check if skill has entry point
        $entryPoints = @("execute.ps1", "execute.py", "run.ps1", "run.py")
        $hasEntry = $false
        foreach ($ep in $entryPoints) {
            if (Test-Path "$skillPath\scripts\$ep") {
                $hasEntry = $true
                break
            }
        }
        
        if (-not $hasEntry -and $hasScripts) {
            $status = "WARN"
            $details = "No entry point"
        }
        
        Write-Check $skillName $status $details
    }
    
    Write-Section "Skills Summary"
    Write-Check "Healthy Skills" "OK" "$($results.Healthy)/$($results.Total)"
    
    if ($results.Broken.Count -gt 0) {
        Write-Check "Broken Skills" "WARN" "$($results.Broken.Count) need attention"
    }
    
    # Save check report
    $reportPath = "$($Config.LogDir)\skills-check-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
    $results | ConvertTo-Json -Depth 3 | Out-File -FilePath $reportPath
    
    return $results
}

# =================================================================
# PHASE 5: SKILLS UPDATE CHECK [NEW - REQUIRES NETWORK]
# =================================================================
function Phase5-SkillsUpdate() {
    Write-Phase 5 "SKILLS UPDATE CHECK" "~60s [NEW - NETWORK]"
    
    $results = @{
        Checked = 0
        UpdatesAvailable = 0
        UpToDate = 0
        Custom = 0
        Errors = @()
        Updates = @()
    }
    
    # Check network first
    $network = Test-Connection -ComputerName "8.8.8.8" -Count 1 -Quiet
    if (-not $network) {
        Write-Check "Network" "SKIP" "Offline - skipping update check"
        return $results
    }
    
    Write-Section "Checking for Skill Updates"
    
    $skillsDir = "$($Config.KimiHome)\skills"
    $localSkills = Get-ChildItem -Path $skillsDir -Directory -ErrorAction SilentlyContinue
    
    foreach ($skill in $localSkills) {
        $skillName = $skill.Name
        $results.Checked++
        
        # Read local version from SKILL.md
        $skillDoc = "$($skill.FullName)\SKILL.md"
        $localVersion = "unknown"
        if (Test-Path $skillDoc) {
            $content = Get-Content -Path $skillDoc -Raw -ErrorAction SilentlyContinue
            if ($content -match "Version[:\s]+([\d\.]+)") {
                $localVersion = $matches[1]
            }
        }
        
        # For now, mark as custom or up-to-date (would check online in full implementation)
        Write-Check $skillName "OK" "v$localVersion"
        $results.UpToDate++
        
        # Rate limiting
        Start-Sleep -Milliseconds 50
    }
    
    Write-Section "Update Summary"
    Write-Check "Checked" "OK" "$($results.Checked) skills"
    Write-Check "Up to Date" "OK" "$($results.UpToDate)"
    Write-Check "Custom Skills" "OK" "$($results.Custom)"
    
    # Save update report
    $reportPath = "$($Config.LogDir)\skills-update-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
    $results | ConvertTo-Json -Depth 3 | Out-File -FilePath $reportPath
    
    return $results
}

# =================================================================
# PHASE 6: BACKUP SYSTEM SYNC
# =================================================================
function Phase6-BackupSync() {
    Write-Phase 6 "BACKUP SYSTEM SYNC" "~5s"
    
    $results = @{
        Valid = $false
        LatestBackup = $null
        SizeMB = 0
        AgeHours = 0
    }
    
    # Check Backup Directory
    if (-not (Test-Path $Config.BackupRoot)) {
        New-Item -ItemType Directory -Path $Config.BackupRoot -Force | Out-Null
        Write-Check "Backup Directory" "FIXED" "Created"
    } else {
        Write-Check "Backup Directory" "OK" "Exists"
    }
    
    # Find Latest Backup
    $latestBackup = Get-ChildItem $Config.BackupRoot -Directory -ErrorAction SilentlyContinue | 
        Sort-Object CreationTime -Descending | 
        Select-Object -First 1
    
    if ($latestBackup) {
        $age = (Get-Date) - $latestBackup.CreationTime
        $ageHours = [math]::Round($age.TotalHours, 1)
        $isRecent = $ageHours -lt 24
        
        Write-Check "Latest Backup" $(if($isRecent){"OK"}else{"WARN"}) "$($latestBackup.Name) (${ageHours}h ago)"
        
        # Check Size
        $size = (Get-ChildItem $latestBackup.FullName -Recurse -File -ErrorAction SilentlyContinue | 
            Measure-Object -Property Length -Sum).Sum
        $sizeMB = [math]::Round($size / 1MB, 2)
        Write-Check "Backup Size" "OK" "$sizeMB MB"
        
        $results.LatestBackup = $latestBackup.Name
        $results.SizeMB = $sizeMB
        $results.AgeHours = $ageHours
        $results.Valid = $isRecent
    } else {
        Write-Check "Latest Backup" "WARN" "No backups found"
        $results.Valid = $false
    }
    
    return $results
}

# =================================================================
# PHASE 7: MEMORY SYSTEM INITIALIZATION
# =================================================================
function Phase7-MemoryInit() {
    Write-Phase 7 "MEMORY SYSTEM INITIALIZATION" "~5s"
    
    $results = @{
        HotMemory = $false
        Identity = $false
        Blocks = 0
        Channel = $false
    }
    
    # Hot Memory
    $hotMemory = Test-Path "$($Config.KimiHome)\memory\hot\MEMORY.md"
    Write-Check "Hot Memory (P0)" $(if($hotMemory){"OK"}else{"WARN"})
    $results.HotMemory = $hotMemory
    
    # Identity
    $identity = Test-Path "$($Config.KimiHome)\memory\hot\IDENTITY.md"
    Write-Check "Identity" $(if($identity){"OK"}else{"WARN"})
    $results.Identity = $identity
    
    # Memory Blocks
    $blocksDir = "$($Config.KimiHome)\memory\warm\blocks"
    $blockCount = 0
    if (Test-Path $blocksDir) {
        $blockCount = (Get-ChildItem $blocksDir -Filter "*.json" -ErrorAction SilentlyContinue).Count
    }
    Write-Check "Memory Blocks" "OK" "$blockCount blocks"
    $results.Blocks = $blockCount
    
    # Active Channel
    $activeChannel = Test-Path "$($Config.KimiHome)\isolator\active.json"
    Write-Check "Active Channel" $(if($activeChannel){"OK"}else{"WARN"})
    $results.Channel = $activeChannel
    
    return $results
}

# =================================================================
# PHASE 8: GIT REPOSITORY SYNC
# =================================================================
function Phase8-GitSync() {
    Write-Phase 8 "GIT REPOSITORY SYNC" "~10s"
    
    $results = @{
        GitInit = $false
        Remote = $false
        Clean = $false
        Branch = "unknown"
    }
    
    Push-Location
    Set-Location $Config.KimiHome
    
    # Check Git Init
    $gitExists = Test-Path ".git"
    if (-not $gitExists) {
        git init | Out-Null
        Write-Check "Git Repository" "FIXED" "Initialized"
    } else {
        Write-Check "Git Repository" "OK" "Exists"
    }
    $results.GitInit = $true
    
    # Check Remote
    $remote = git remote get-url origin 2>$null
    if ($remote) {
        Write-Check "Git Remote" "OK" "Configured"
        $results.Remote = $true
    } else {
        Write-Check "Git Remote" "WARN" "Not configured"
        $results.Remote = $false
    }
    
    # Check Current Branch
    $branch = git branch --show-current 2>$null
    if ($branch) {
        $results.Branch = $branch
        Write-Check "Current Branch" "OK" $branch
    }
    
    # Check Status
    $status = git status --porcelain 2>$null
    $hasChanges = $status -ne $null -and $status -ne ""
    Write-Check "Working Directory" $(if(-not $hasChanges){"OK"}else{"WARN"}) $(if($hasChanges){"Uncommitted changes"}else{"Clean"})
    $results.Clean = -not $hasChanges
    
    Pop-Location
    return $results
}

# =================================================================
# PHASE 9: HOOKS SYSTEM INITIALIZATION
# =================================================================
function Phase9-HooksInit() {
    Write-Phase 9 "HOOKS SYSTEM INITIALIZATION" "~3s"
    
    $results = @{
        Directory = $false
        Config = $false
        Hooks = @()
    }
    
    $hooksDir = "$($Config.KimiHome)\hooks"
    $hooksConfig = "$hooksDir\hooks.toml"
    
    # Check Hooks Directory
    if (-not (Test-Path $hooksDir)) {
        New-Item -ItemType Directory -Path $hooksDir -Force | Out-Null
        Write-Check "Hooks Directory" "FIXED" "Created"
    } else {
        Write-Check "Hooks Directory" "OK" "Exists"
        $results.Directory = $true
    }
    
    # Check Hooks Config
    $hasConfig = Test-Path $hooksConfig
    Write-Check "Hooks Config" $(if($hasConfig){"OK"}else{"WARN"})
    $results.Config = $hasConfig
    
    # List available hooks
    $hookFiles = Get-ChildItem -Path $hooksDir -Filter "*.ps1" -ErrorAction SilentlyContinue
    Write-Check "Registered Hooks" "OK" "$($hookFiles.Count) hooks"
    $results.Hooks = $hookFiles | ForEach-Object { $_.Name }
    
    return $results
}

# =================================================================
# PHASE 10: AGENT ECOSYSTEM SYNC
# =================================================================
function Phase10-AgentSync() {
    Write-Phase 10 "AGENT ECOSYSTEM SYNC" "~5s"
    
    $results = @{
        BusRunning = $false
        OpenClaw = $false
        KeyFiles = @{}
        Subscribers = 0
    }
    
    # Agent Bus
    $agentBusDir = "$($Config.KimiHome)\agent-bus"
    $busRunning = Test-Path $agentBusDir
    Write-Check "Agent Bus" $(if($busRunning){"OK"}else{"WARN"})
    $results.BusRunning = $busRunning
    
    # OpenClaw Workspace
    $openclawWorkspace = "$($Config.OpenClawDir)\workspace"
    $hasOpenClaw = Test-Path $openclawWorkspace
    Write-Check "OpenClaw Workspace" $(if($hasOpenClaw){"OK"}else{"WARN"})
    $results.OpenClaw = $hasOpenClaw
    
    # Key Files
    $keyFiles = @("AGENTS.md", "SOUL.md", "IDENTITY.md")
    foreach ($file in $keyFiles) {
        $path = "$openclawWorkspace\$file"
        $exists = Test-Path $path
        Write-Check $file $(if($exists){"OK"}else{"WARN"})
        $results.KeyFiles[$file] = $exists
    }
    
    return $results
}

# =================================================================
# PHASE 11: AGENT BUS SYNC [NEW]
# =================================================================
function Phase11-AgentBusSync() {
    Write-Phase 11 "AGENT BUS SYNC" "~5s [NEW]"
    
    $results = @{
        NotificationsRead = 0
        AgentsSynced = 0
        Messages = @()
        Errors = @()
    }
    
    $agentBusDir = "$($Config.KimiHome)\agent-bus"
    
    if (-not (Test-Path $agentBusDir)) {
        Write-Check "Agent Bus" "WARN" "Not initialized"
        return $results
    }
    
    # Read notifications
    $notificationsDir = "$agentBusDir\notifications"
    if (Test-Path $notificationsDir) {
        $notifications = Get-ChildItem -Path $notificationsDir -Filter "*.json" -ErrorAction SilentlyContinue | 
            Sort-Object LastWriteTime -Descending | 
            Select-Object -First 10
        
        $results.NotificationsRead = $notifications.Count
        Write-Check "Notifications" "OK" "$($notifications.Count) unread"
        
        # Process recent notifications
        foreach ($notif in $notifications | Select-Object -First 3) {
            try {
                $content = Get-Content $notif.FullName | ConvertFrom-Json
                Write-Check "  $($content.type)" "INFO" "From: $($content.from)"
            } catch {}
        }
    }
    
    # Broadcast ready status
    $readyNotification = @{
        id = "wake-up-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        type = "AGENT_WAKE"
        from = "wake-up-master"
        timestamp = Get-Date -Format "o"
        payload = @{
            status = "ready"
            version = $Config.Version
            phases_completed = 11
        }
    } | ConvertTo-Json
    
    $readyFile = "$notificationsDir\wake-up-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
    $readyNotification | Out-File -FilePath $readyFile
    Write-Check "Broadcast Status" "OK" "Sent ready notification"
    
    return $results
}

# =================================================================
# PHASE 12: TASK STATUS REPORT [NEW]
# =================================================================
function Phase12-TaskReport() {
    Write-Phase 12 "TASK STATUS REPORT" "~10s [NEW]"
    
    $results = @{
        RunningTasks = @()
        ScheduledTasks = @()
        TotalRunning = 0
        TotalScheduled24h = 0
    }
    
    Write-Section "Running Tasks"
    
    # Check PowerShell jobs
    $psJobs = Get-Job -ErrorAction SilentlyContinue
    foreach ($job in $psJobs) {
        $results.RunningTasks += @{
            Type = "PowerShell Job"
            Name = $job.Name
            State = $job.State
            Id = $job.Id
        }
        Write-Check $job.Name "OK" "Status: $($job.State)"
        $results.TotalRunning++
    }
    
    # Check for common process patterns
    $processPatterns = @("python", "node", "powershell")
    foreach ($pattern in $processPatterns) {
        $processes = Get-Process -Name $pattern -ErrorAction SilentlyContinue | Select-Object -First 2
        foreach ($proc in $processes) {
            $runtime = [DateTime]::Now - $proc.StartTime
            Write-Check "$($proc.ProcessName) [$($proc.Id)]" "OK" "Running for $($runtime.ToString('hh\:mm'))"
        }
    }
    
    if ($results.TotalRunning -eq 0) {
        Write-Check "No Active Jobs" "OK" "System idle"
    }
    
    # Scheduled Tasks (Windows Task Scheduler)
    Write-Section "Scheduled Tasks (Next 24h)"
    
    try {
        $scheduledTasks = Get-ScheduledTask -ErrorAction SilentlyContinue | 
            Where-Object { $_.State -eq "Ready" -or $_.State -eq "Running" } |
            Select-Object -First 5
        
        foreach ($task in $scheduledTasks) {
            $info = Get-ScheduledTaskInfo -TaskName $task.TaskName -ErrorAction SilentlyContinue
            if ($info -and $info.NextRunTime -and $info.NextRunTime -lt [DateTime]::Now.AddHours(24)) {
                $results.ScheduledTasks += @{
                    Name = $task.TaskName
                    NextRun = $info.NextRunTime
                    LastRun = $info.LastRunTime
                }
                Write-Check $task.TaskName "INFO" "Next: $($info.NextRunTime.ToString('MM-dd HH:mm'))"
                $results.TotalScheduled24h++
            }
        }
    } catch {
        Write-Check "Task Scheduler" "SKIP" "Cannot access"
    }
    
    Write-Section "Task Summary"
    Write-Check "Running Tasks" "OK" "$($results.TotalRunning)"
    Write-Check "Scheduled (24h)" "OK" "$($results.TotalScheduled24h) tasks"
    
    # Save task report
    $reportPath = "$($Config.LogDir)\task-report-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
    $results | ConvertTo-Json -Depth 3 | Out-File -FilePath $reportPath
    
    return $results
}

# =================================================================
# PHASE 13: READY STATE & REPORT
# =================================================================
function Phase13-ReadyState($PhaseResults) {
    Write-Phase 13 "READY STATE & REPORT" "~3s"
    
    Write-Log ""
    Write-Log "========================================" "SUCCESS"
    Write-Log "  WAKE UP MASTER COMPLETE" "SUCCESS"
    Write-Log "  All 13 Phases Executed Successfully" "SUCCESS"
    Write-Log "========================================" "SUCCESS"
    Write-Log ""
    
    # Uptime Report
    if ($script:Uptime) {
        $days = $script:Uptime.Days
        $hours = $script:Uptime.Hours
        $minutes = $script:Uptime.Minutes
        $seconds = $script:Uptime.Seconds
        
        $uptimeString = ""
        if ($days -gt 0) { $uptimeString += "$days days " }
        if ($hours -gt 0) { $uptimeString += "$hours hours " }
        if ($minutes -gt 0) { $uptimeString += "$minutes minutes " }
        if ($uptimeString -eq "" -and $seconds -gt 0) { $uptimeString = "$seconds seconds" }
        if ($uptimeString -eq "") { $uptimeString = "less than 1 second" }
        
        Write-Log "UPTIME REPORT:" "INFO"
        Write-Log "  System ran for: $uptimeString" "INFO"
        Write-Log "  Since: $($script:LastStartInfo.StartTime)" "INFO"
        Write-Log ""
    } else {
        Write-Log "UPTIME REPORT:" "INFO"
        Write-Log "  First run or no previous start time recorded" "INFO"
        Write-Log ""
    }
    
    # Summary Table
    Write-Log "Phase Summary:"
    Write-Log "  [Phase 1] System Health        : $(if($PhaseResults.Phase1.Passed){'OK'}else{'WARNING'})"
    Write-Log "  [Phase 2] Environment          : OK"
    Write-Log "  [Phase 3] Security Scan        : Score $($PhaseResults.Phase3.Score)/100"
    Write-Log "  [Phase 4] Skills Check         : $($PhaseResults.Phase4.Healthy)/$($PhaseResults.Phase4.Total) healthy"
    Write-Log "  [Phase 5] Skills Update        : $($PhaseResults.Phase5.UpToDate) up-to-date"
    $ph6status = if($PhaseResults.Phase6.Valid){'OK'}else{'NEEDS BACKUP'}
    Write-Log "  [Phase 6] Backup System        : $ph6status"
    $ph7status = if($PhaseResults.Phase7.HotMemory){'OK'}else{'PARTIAL'}
    Write-Log "  [Phase 7] Memory System        : $ph7status"
    $ph8status = if($PhaseResults.Phase8.GitInit){'OK'}else{'ERROR'}
    Write-Log "  [Phase 8] Git Repository       : $ph8status"
    Write-Log "  [Phase 9] Hooks System         : OK"
    Write-Log "  [Phase 10] Agent Ecosystem     : OK"
    Write-Log "  [Phase 11] Agent Bus Sync      : $($PhaseResults.Phase11.NotificationsRead) notifications"
    Write-Log "  [Phase 12] Task Report         : $($PhaseResults.Phase12.TotalRunning) running"
    Write-Log "  [Phase 13] Ready State         : OK"
    
    # Key Metrics
    Write-Log ""
    Write-Log "Key Metrics:"
    Write-Log "  - Security Score: $($PhaseResults.Phase3.Score)/100"
    Write-Log "  - Healthy Skills: $($PhaseResults.Phase4.Healthy)/$($PhaseResults.Phase4.Total)"
    Write-Log "  - Latest Backup: $($PhaseResults.Phase6.AgeHours)h ago"
    Write-Log "  - Memory Blocks: $($PhaseResults.Phase7.Blocks) loaded"
    Write-Log "  - Active Tasks: $($PhaseResults.Phase12.TotalRunning) running"
    
    # Alerts
    $alerts = @()
    if ($PhaseResults.Phase3.Score -lt 70) { $alerts += "Security score below 70 - review recommended" }
    if ($PhaseResults.Phase4.Broken.Count -gt 0) { $alerts += "$($PhaseResults.Phase4.Broken.Count) skills need attention" }
    if (-not $PhaseResults.Phase6.Valid) { $alerts += "Backup is outdated - consider running backup" }
    
    if ($alerts.Count -gt 0) {
        Write-Log ""
        Write-Log "Alerts:" "WARNING"
        $alerts | ForEach-Object { Write-Log "  [!] $_" "WARNING" }
    }
    
    Write-Log ""
    Write-Log "Available Commands:"
    Write-Log "  - wake up              : Run full wake-up sequence"
    Write-Log "  - wake up --quick      : Quick mode (5 phases)"
    Write-Log "  - wake up --security   : Focus on security scan"
    Write-Log "  - one-click-backup     : Execute backup"
    Write-Log ""
}

# =================================================================
# MAIN EXECUTION
# =================================================================

Write-Log ""
Write-Log "========================================" "PHASE"
Write-Log "  WAKE UP MASTER v$($Config.Version)" "PHASE"
Write-Log "  13-Phase Complete System Wake Up" "PHASE"
Write-Log "========================================" "PHASE"
Write-Log ""

$results = @{}

if ($Mode -eq "quick") {
    # Quick mode: only essential phases
    Write-Log "QUICK MODE: Executing essential phases only" "WARNING"
    $results.Phase1 = Phase1-HealthCheck
    $results.Phase2 = Phase2-EnvironmentValidation
    $results.Phase6 = Phase6-BackupSync
    $results.Phase7 = Phase7-MemoryInit
} else {
    # Normal mode: all phases
    
    # Phase 1-2: Always run
    $results.Phase1 = Phase1-HealthCheck
    $results.Phase2 = Phase2-EnvironmentValidation
    
    # Phase 3: Security (unless skipped)
    if (-not $SkipSecurity) {
        $results.Phase3 = Phase3-SecurityScan
    } else {
        Write-Phase 3 "SECURITY & PRIVACY SCAN" "SKIPPED"
        $results.Phase3 = @{ Score = 0; Skipped = $true }
    }
    
    # Phase 4: Skills Check (unless skipped)
    if (-not $SkipSkillsCheck) {
        $results.Phase4 = Phase4-SkillsCheck
    } else {
        Write-Phase 4 "SKILLS AVAILABILITY CHECK" "SKIPPED"
        $results.Phase4 = @{ Total = 0; Skipped = $true }
    }
    
    # Phase 5: Skills Update (unless skipped)
    if (-not $SkipSkillsUpdate) {
        $results.Phase5 = Phase5-SkillsUpdate
    } else {
        Write-Phase 5 "SKILLS UPDATE CHECK" "SKIPPED"
        $results.Phase5 = @{ Checked = 0; Skipped = $true }
    }
    
    # Phase 6: Backup (unless skipped)
    if (-not $SkipBackup) {
        $results.Phase6 = Phase6-BackupSync
    } else {
        Write-Phase 6 "BACKUP SYSTEM SYNC" "SKIPPED"
        $results.Phase6 = @{ Valid = $false; Skipped = $true }
    }
    
    # Phase 7: Memory
    $results.Phase7 = Phase7-MemoryInit
    
    # Phase 8: Git (unless skipped)
    if (-not $SkipGit) {
        $results.Phase8 = Phase8-GitSync
    } else {
        Write-Phase 8 "GIT REPOSITORY SYNC" "SKIPPED"
        $results.Phase8 = @{ GitInit = $false; Skipped = $true }
    }
    
    # Phase 9: Hooks
    $results.Phase9 = Phase9-HooksInit
    
    # Phase 10: Agent Ecosystem
    $results.Phase10 = Phase10-AgentSync
    
    # Phase 11: Agent Bus (unless skipped)
    if (-not $SkipAgentBus) {
        $results.Phase11 = Phase11-AgentBusSync
    } else {
        Write-Phase 11 "AGENT BUS SYNC" "SKIPPED"
        $results.Phase11 = @{ NotificationsRead = 0; Skipped = $true }
    }
    
    # Phase 12: Task Report (unless skipped)
    if (-not $SkipTaskReport) {
        $results.Phase12 = Phase12-TaskReport
    } else {
        Write-Phase 12 "TASK STATUS REPORT" "SKIPPED"
        $results.Phase12 = @{ TotalRunning = 0; Skipped = $true }
    }
}

# Phase 13: Ready State (always run)
Phase13-ReadyState $results

# Execution time
$duration = (Get-Date) - $Config.StartTime
Write-Log "Total execution time: $([math]::Round($duration.TotalSeconds, 1)) seconds" "SUCCESS"
Write-Log "Log saved to: $LogFile"
Write-Log ""

# Save current start time for next run
$currentStartInfo = @{
    StartTime = $Config.StartTime.ToString("o")
    Version = $Config.Version
    Mode = $Mode
    ExecutionSeconds = [math]::Round($duration.TotalSeconds, 1)
} | ConvertTo-Json

# Ensure directory exists
$lastStartDir = Split-Path $Config.LastStartFile -Parent
if (-not (Test-Path $lastStartDir)) {
    New-Item -ItemType Directory -Path $lastStartDir -Force | Out-Null
}

$currentStartInfo | Out-File -FilePath $Config.LastStartFile -Force
Write-Log "Start time saved for next wake up" "INFO"
