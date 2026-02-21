# GitHub推送脚本
# 用于将 Godlike Kimi Skills 项目推送到 GitHub

param(
    [string]$OrganizationName = "godlike-kimi-skills",
    [string]$RepoName = "godlike-kimi-skills",
    [switch]$Force = $false
)

$ErrorActionPreference = "Stop"

# 颜色输出函数
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# 项目路径
$ProjectPath = "D:\kimi\projects\godlike-kimi-skills"

Write-ColorOutput "🌙 Godlike Kimi Skills - GitHub 推送脚本" "Cyan"
Write-ColorOutput "========================================" "Cyan"
Write-ColorOutput ""

# 检查项目目录是否存在
if (-not (Test-Path $ProjectPath)) {
    Write-ColorOutput "❌ 错误: 项目路径不存在: $ProjectPath" "Red"
    exit 1
}

# 进入项目目录
Set-Location $ProjectPath
Write-ColorOutput "📁 项目路径: $ProjectPath" "Gray"
Write-ColorOutput ""

# 检查 Git 是否安装
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-ColorOutput "❌ 错误: Git 未安装或未添加到 PATH" "Red"
    exit 1
}

# 检查是否已初始化 Git
if (-not (Test-Path ".git")) {
    Write-ColorOutput "📦 初始化 Git 仓库..." "Yellow"
    git init
    Write-ColorOutput "✅ Git 仓库初始化完成" "Green"
} else {
    Write-ColorOutput "✅ Git 仓库已存在" "Green"
}

Write-ColorOutput ""

# 检查 Git 配置
$userName = git config user.name
$userEmail = git config user.email

if (-not $userName -or -not $userEmail) {
    Write-ColorOutput "⚠️ 警告: Git 用户信息未配置" "Yellow"
    Write-ColorOutput "   请运行以下命令配置:" "Gray"
    Write-ColorOutput '   git config --global user.name "Your Name"' "Gray"
    Write-ColorOutput '   git config --global user.email "your@email.com"' "Gray"
    exit 1
}

Write-ColorOutput "👤 Git 用户: $userName <$userEmail>" "Gray"
Write-ColorOutput ""

# 添加所有文件
Write-ColorOutput "➕ 添加文件到暂存区..." "Yellow"
git add .
Write-ColorOutput "✅ 文件添加完成" "Green"
Write-ColorOutput ""

# 检查是否有变更需要提交
$status = git status --porcelain
if (-not $status) {
    Write-ColorOutput "⚠️ 没有需要提交的变更" "Yellow"
} else {
    # 提交变更
    Write-ColorOutput "📝 提交变更..." "Yellow"
    git commit -m "🚀 Initial commit: 224+ production-ready skills for Kimi CLI"
    Write-ColorOutput "✅ 提交完成" "Green"
}

Write-ColorOutput ""

# 重命名主分支为 main
$currentBranch = git branch --show-current
if ($currentBranch -ne "main") {
    Write-ColorOutput "🔄 重命名分支为 main..." "Yellow"
    git branch -M main
    Write-ColorOutput "✅ 分支重命名完成" "Green"
} else {
    Write-ColorOutput "✅ 已在 main 分支" "Green"
}

Write-ColorOutput ""

# 检查远程仓库
$remoteUrl = "https://github.com/$OrganizationName/$RepoName.git"
$existingRemote = git remote -v 2>$null

if ($existingRemote -match "origin") {
    Write-ColorOutput "🌐 远程仓库已存在" "Yellow"
    git remote set-url origin $remoteUrl
    Write-ColorOutput "✅ 远程仓库 URL 已更新: $remoteUrl" "Green"
} else {
    Write-ColorOutput "🔗 添加远程仓库..." "Yellow"
    git remote add origin $remoteUrl
    Write-ColorOutput "✅ 远程仓库添加完成: $remoteUrl" "Green"
}

Write-ColorOutput ""

# 推送到 GitHub
Write-ColorOutput "📤 推送到 GitHub..." "Yellow"
Write-ColorOutput "   远程地址: $remoteUrl" "Gray"
Write-ColorOutput ""

try {
    if ($Force) {
        git push -u origin main --force
    } else {
        git push -u origin main
    }
    Write-ColorOutput ""
    Write-ColorOutput "✅ 推送成功!" "Green"
    Write-ColorOutput ""
    Write-ColorOutput "🎉 项目已成功推送到 GitHub!" "Green"
    Write-ColorOutput "   URL: https://github.com/$OrganizationName/$RepoName" "Cyan"
} catch {
    Write-ColorOutput ""
    Write-ColorOutput "❌ 推送失败" "Red"
    Write-ColorOutput "   错误信息: $_" "Red"
    Write-ColorOutput ""
    Write-ColorOutput "💡 可能的解决方案:" "Yellow"
    Write-ColorOutput "   1. 确认 GitHub 组织/仓库已创建" "Gray"
    Write-ColorOutput "   2. 检查网络连接" "Gray"
    Write-ColorOutput "   3. 确认有写入权限" "Gray"
    Write-ColorOutput "   4. 使用 -Force 参数强制推送 (谨慎使用)" "Gray"
    exit 1
}

Write-ColorOutput ""
Write-ColorOutput "📋 下一步操作:" "Cyan"
Write-ColorOutput "   1. 访问仓库设置 Topics 标签" "Gray"
Write-ColorOutput "   2. 创建第一个 Release" "Gray"
Write-ColorOutput "   3. 启用 Discussions" "Gray"
Write-ColorOutput ""
Write-ColorOutput "📖 详细指南请查看: GITHUB_RELEASE_CHECKLIST.md" "Gray"
