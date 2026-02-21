#!/usr/bin/env powershell
# Godlike Kimi Skills - 一键发布执行脚本
# 执行方式: 以管理员身份运行 PowerShell，然后执行 .\EXECUTE_NOW.ps1

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     🚀 Godlike Kimi Skills - 一键发布执行脚本                ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# 检查Git
Write-Host "🔍 检查Git安装..." -ForegroundColor Yellow
$gitExists = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitExists) {
    Write-Host "❌ Git未安装！请先安装Git: https://git-scm.com/download/win" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Git已安装" -ForegroundColor Green

# 设置变量
$ProjectPath = "D:\kimi\projects\godlike-kimi-skills"
$OrgName = "godlike-kimi-skills"
$RepoName = "awesome-kimi-skills"

Write-Host ""
Write-Host "📁 项目路径: $ProjectPath" -ForegroundColor White
Write-Host "🌐 GitHub组织: $OrgName" -ForegroundColor White
Write-Host "📦 仓库名称: $RepoName" -ForegroundColor White
Write-Host ""

# 步骤1: Git初始化
Write-Host "【步骤1/5】初始化Git仓库..." -ForegroundColor Yellow
Set-Location $ProjectPath

if (Test-Path ".git") {
    Write-Host "⚠️ Git仓库已存在，跳过初始化" -ForegroundColor Yellow
} else {
    git init
    Write-Host "✅ Git仓库初始化完成" -ForegroundColor Green
}

# 步骤2: 配置Git
Write-Host ""
Write-Host "【步骤2/5】配置Git用户信息..." -ForegroundColor Yellow
$gitUserName = git config user.name
$gitUserEmail = git config user.email

if (-not $gitUserName) {
    $defaultName = "Kbot"
    $gitUserName = Read-Host "请输入Git用户名 (默认: $defaultName)"
    if (-not $gitUserName) { $gitUserName = $defaultName }
    git config user.name "$gitUserName"
}

if (-not $gitUserEmail) {
    $defaultEmail = "kbot@godlike-kimi.dev"
    $gitUserEmail = Read-Host "请输入Git邮箱 (默认: $defaultEmail)"
    if (-not $gitUserEmail) { $gitUserEmail = $defaultEmail }
    git config user.email "$gitUserEmail"
}

Write-Host "✅ Git用户: $gitUserName <$gitUserEmail>" -ForegroundColor Green

# 步骤3: 添加文件
Write-Host ""
Write-Host "【步骤3/5】添加文件到Git..." -ForegroundColor Yellow
git add .
$status = git status --short
$fileCount = ($status -split "`n" | Where-Object { $_ -ne "" }).Count
Write-Host "✅ 已添加 $fileCount 个文件到暂存区" -ForegroundColor Green

# 步骤4: 提交
Write-Host ""
Write-Host "【步骤4/5】提交代码..." -ForegroundColor Yellow
$commitMessage = "🚀 Initial commit: 20 production-ready skills for Kimi CLI

- 20 high-quality production-grade skills
- Full CI/CD automation
- Chinese-optimized documentation
- 80%+ test coverage
- MIT License

Skills include:
- webapp-testing, static-analysis (NEW)
- skill-creator-enhanced, mcp-builder
- docx-skill, pdf-skill, xlsx-skill, pptx-skill
- browser-use-skill, systematic-debugging
- And 10 more..."

git commit -m "$commitMessage"
Write-Host "✅ 代码提交完成" -ForegroundColor Green

# 步骤5: 推送到GitHub
Write-Host ""
Write-Host "【步骤5/5】推送到GitHub..." -ForegroundColor Yellow
Write-Host ""
Write-Host "⚠️ 请先确保已在GitHub创建了组织和仓库！" -ForegroundColor Yellow
Write-Host "   组织: https://github.com/$OrgName" -ForegroundColor White
Write-Host "   仓库: https://github.com/$OrgName/$RepoName" -ForegroundColor White
Write-Host ""

$continue = Read-Host "是否继续推送? (y/n)"
if ($continue -ne "y") {
    Write-Host "⏸️ 推送已取消，您可以稍后手动执行:" -ForegroundColor Yellow
    Write-Host "   git push -u origin main" -ForegroundColor White
    exit 0
}

# 检查远程仓库
$remoteExists = git remote | Select-String "origin"
if ($remoteExists) {
    git remote remove origin
}

git remote add origin "https://github.com/$OrgName/$RepoName.git"
Write-Host "✅ 远程仓库已添加" -ForegroundColor Green

try {
    git branch -M main
    git push -u origin main
    Write-Host ""
    Write-Host "🎉 推送成功！" -ForegroundColor Green
    Write-Host ""
    Write-Host "📍 GitHub地址: https://github.com/$OrgName/$RepoName" -ForegroundColor Cyan
} catch {
    Write-Host ""
    Write-Host "❌ 推送失败！可能的原因:" -ForegroundColor Red
    Write-Host "   1. GitHub组织/仓库尚未创建" -ForegroundColor Yellow
    Write-Host "   2. 网络连接问题" -ForegroundColor Yellow
    Write-Host "   3. 权限不足" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "请创建组织后手动执行:" -ForegroundColor White
    Write-Host "   git push -u origin main" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "                     执行完成！                               " -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# 显示后续步骤
Write-Host "📋 后续手动操作步骤:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. 🔴 创建GitHub组织:" -ForegroundColor White
Write-Host "   https://github.com/account/organizations/new" -ForegroundColor Cyan
Write-Host "   组织名: godlike-kimi-skills" -ForegroundColor Gray
Write-Host ""
Write-Host "2. 🔴 创建GitHub仓库:" -ForegroundColor White
Write-Host "   https://github.com/new" -ForegroundColor Cyan
Write-Host "   仓库名: awesome-kimi-skills" -ForegroundColor Gray
Write-Host ""
Write-Host "3. 🟡 注册Gitee:" -ForegroundColor White
Write-Host "   https://gitee.com/signup" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. 🟡 发布推广:" -ForegroundColor White
Write-Host "   - V2EX: 复制 docs/promotion/v2ex-launch.md" -ForegroundColor Gray
Write-Host "   - 掘金: 复制 docs/promotion/juejin-article.md" -ForegroundColor Gray
Write-Host "   - Twitter: 复制 docs/promotion/twitter-launch.md" -ForegroundColor Gray
Write-Host ""

Read-Host "按Enter键退出"
