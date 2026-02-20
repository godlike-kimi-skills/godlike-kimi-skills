#!/usr/bin/env pwsh
# Quick Postmortem Generator
# 快速复盘文档生成器
# 用法: .\generate-postmortem.ps1 -ProjectName "WinSage" -Result "Failed" -Reason "Platform mismatch"

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectName,
    
    [Parameter(Mandatory=$true)]
    [ValidateSet("Success", "Failed", "Paused", "Cancelled")]
    [string]$Result,
    
    [string]$Reason = "",
    [string]$StartDate = "",
    [string]$EndDate = (Get-Date -Format "yyyy-MM-dd"),
    [string]$OutputPath = "D:\kimi\business-memory"
)

$ErrorActionPreference = "Continue"

# Determine emoji based on result
$resultEmoji = switch ($Result) {
    "Success" { "✅" }
    "Failed" { "❌" }
    "Paused" { "⏸️" }
    "Cancelled" { "🚫" }
}

# Generate filename
$filename = "postmortem-$($ProjectName.ToLower())-$($EndDate.Replace('-', '')).md"
$filepath = Join-Path $OutputPath $filename

# Build content
$content = @"
# $ProjectName 项目复盘报告
## Postmortem: $ProjectName

**项目结果:** $resultEmoji $Result  
**结束日期:** $EndDate  
**结束原因:** $Reason  

---

## 执行摘要

### 项目概况
- **项目名称:** $ProjectName
- **开始时间:** $StartDate
- **结束时间:** $EndDate
- **项目结果:** $Result
- **结束原因:** $Reason

### 关键数据
- 总投入: （待填写）
- 产出结果: （待填写）
- ROI: （待填写）

---

## 详细时间线

| 时间 | 事件 | 决策/结果 |
|------|------|----------|
| $StartDate | 项目启动 | 开始执行 |
| | | |
| $EndDate | 项目$Result | 结束原因: $Reason |

---

## 根本原因分析

### 5 Whys 分析
1. **为什么项目$Result?**
   - 

2. **为什么发生上述情况?**
   - 

3. **为什么会出现这种情况?**
   - 

4. **为什么会导致这种问题?**
   - 

5. **根本原因是什么?**
   - 

### 使用的分析框架
- [ ] First Principles Thinking
- [ ] Lean Startup Analysis
- [ ] Cold Start Theory
- [ ] SWOT Analysis
- [ ] Other: 

---

## 做得好的地方（Keep）

1. 
2. 
3. 

## 需要改进的地方（Problem）

1. 
2. 
3. 

## 应该开始做的事（Start）

1. 
2. 
3. 

## 应该停止做的事（Stop）

1. 
2. 
3. 

---

## 关键教训

### 技术教训
- 

### 业务教训
- 

### 流程教训
- 

### 决策教训
- 

---

## 清理确认

- [ ] 后台任务已删除
- [ ] 定时任务已清理
- [ ] 进程已停止
- [ ] 敏感数据已删除
- [ ] 文件已归档
- [ ] 文档已创建

**验证命令:**
```powershell
.\verify-closure.ps1 -ProjectName "$ProjectName"
```

---

## 行动建议

### 即时行动（24小时内）
- [ ] 

### 短期行动（本周内）
- [ ] 

### 长期行动（本月内）
- [ ] 

---

## 附录

### 相关文件
- 复盘文档: $filepath
- 教训总结: lessons-learned-$($ProjectName.ToLower()).md
- 归档位置: archive/$ProjectName-$($EndDate.Replace('-', ''))/

### 相关项目
- 

### 参考资源
- 

---

**文档生成时间:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")  
**生成工具:** project-postmortem skill  
**下次回顾日期:** （建议30天后回顾此复盘）

---

*"不吸取教训的人注定重蹈覆辙。"*
"@

# Write to file
$content | Out-File -FilePath $filepath -Encoding UTF8

Write-Host ""
Write-Host "===============================================================" -ForegroundColor Green
Write-Host "  Postmortem Generated Successfully!" -ForegroundColor Green
Write-Host "===============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Project: $ProjectName" -ForegroundColor Cyan
Write-Host "  Result: $resultEmoji $Result" -ForegroundColor Cyan
Write-Host "  File: $filepath" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Next steps:" -ForegroundColor Yellow
Write-Host "  1. Edit the file to fill in details" -ForegroundColor White
Write-Host "  2. Run cleanup verification:" -ForegroundColor White
Write-Host "     .\verify-closure.ps1 -ProjectName '$ProjectName'" -ForegroundColor Gray
Write-Host ""
Write-Host "===============================================================" -ForegroundColor Green

# Return filepath for further use
return $filepath
