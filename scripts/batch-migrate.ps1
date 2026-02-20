#!/usr/bin/env pwsh
# 批量迁移现有skills到新仓库

param(
    [string]$SourceDir = "$env:USERPROFILE\.kimi\skills",
    [string]$TargetDir = "D:\kimi\projects\godlike-kimi-skills\skills",
    [int]$Limit = 100
)

$stats = @{
    Total = 0
    Migrated = 0
    Failed = 0
    Skipped = 0
}

# 获取所有skills
$skillDirs = Get-ChildItem -Path $SourceDir -Directory | Select-Object -First $Limit
$stats.Total = $skillDirs.Count

Write-Host "═══════════════════════════════════════════════════════════"
Write-Host "     批量迁移Skills"
Write-Host "═══════════════════════════════════════════════════════════"
Write-Host "源目录: $SourceDir"
Write-Host "目标目录: $TargetDir"
Write-Host "计划迁移: $($stats.Total) 个skills"
Write-Host "═══════════════════════════════════════════════════════════"
Write-Host ""

foreach ($skillDir in $skillDirs) {
    $skillName = $skillDir.Name
    $targetPath = Join-Path $TargetDir $skillName
    
    # 检查是否已存在
    if (Test-Path $targetPath) {
        Write-Host "⏭️  跳过 (已存在): $skillName"
        $stats.Skipped++
        continue
    }
    
    try {
        # 复制目录
        Copy-Item -Path $skillDir.FullName -Destination $targetPath -Recurse -Force
        
        # 处理SKILL.md添加中文描述
        $skillMdPath = Join-Path $targetPath "SKILL.md"
        if (Test-Path $skillMdPath) {
            # 这里可以添加中文描述处理逻辑
            # 暂时保持原样
        }
        
        Write-Host "✅ 已迁移: $skillName"
        $stats.Migrated++
    }
    catch {
        Write-Host "❌ 失败: $skillName - $($_.Exception.Message)"
        $stats.Failed++
    }
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════"
Write-Host "迁移完成!"
Write-Host "═══════════════════════════════════════════════════════════"
Write-Host "总计: $($stats.Total)"
Write-Host "成功: $($stats.Migrated)"
Write-Host "失败: $($stats.Failed)"
Write-Host "跳过: $($stats.Skipped)"
Write-Host "═══════════════════════════════════════════════════════════"
