# Gitee 仓库初始化脚本
# 用于手动同步 GitHub 到 Gitee
# 使用方法: .\init-gitee.ps1

param(
    [string]$GitHubRepo = "godlike-kimi-skills/awesome-kimi-skills",
    [string]$GiteeRepo = "godlike-kimi-skills/awesome-kimi-skills",
    [string]$TempDir = "$env:TEMP\gitee-sync"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Gitee 仓库初始化脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 git 是否安装
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "错误: Git 未安装，请先安装 Git"
    exit 1
}

# 清理临时目录
Write-Host "[1/6] 清理临时目录..." -ForegroundColor Yellow
if (Test-Path $TempDir) {
    Remove-Item -Recurse -Force $TempDir
}
New-Item -ItemType Directory -Path $TempDir -Force | Out-Null

# 克隆 GitHub 仓库
Write-Host "[2/6] 克隆 GitHub 仓库..." -ForegroundColor Yellow
$githubUrl = "https://github.com/$GitHubRepo.git"
try {
    git clone --mirror $githubUrl "$TempDir\repo.git"
    if ($LASTEXITCODE -ne 0) {
        throw "克隆失败"
    }
} catch {
    Write-Error "克隆 GitHub 仓库失败: $_"
    exit 1
}

# 进入仓库目录
Set-Location "$TempDir\repo.git"

# 检查 Gitee 远程仓库是否存在
Write-Host "[3/6] 检查 Gitee 仓库..." -ForegroundColor Yellow
$giteeUrl = "git@gitee.com:$GiteeRepo.git"

# 测试 SSH 连接
Write-Host "      测试 Gitee SSH 连接..." -ForegroundColor Gray
$sshTest = ssh -T git@gitee.com 2>&1
if ($LASTEXITCODE -ne 1) {
    Write-Warning "SSH 连接测试失败，请确保:"
    Write-Warning "  1. 已生成 SSH Key"
    Write-Warning "  2. 已将公钥添加到 Gitee"
    Write-Warning "  3. SSH 服务正常运行"
}

# 添加 Gitee 远程
Write-Host "[4/6] 配置 Gitee 远程仓库..." -ForegroundColor Yellow
git remote add gitee $giteeUrl 2>$null
if ($LASTEXITCODE -ne 0) {
    git remote set-url gitee $giteeUrl
}

# 推送到 Gitee
Write-Host "[5/6] 推送到 Gitee..." -ForegroundColor Yellow
try {
    # 推送所有分支
    git push gitee --all
    if ($LASTEXITCODE -ne 0) {
        throw "推送分支失败"
    }
    
    # 推送所有标签
    git push gitee --tags
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "推送标签失败，但分支已同步"
    }
} catch {
    Write-Error "推送到 Gitee 失败: $_"
    Write-Host ""
    Write-Host "可能的解决方案:" -ForegroundColor Yellow
    Write-Host "  1. 确认 Gitee 仓库已创建"
    Write-Host "  2. 确认 SSH Key 已添加到 Gitee"
    Write-Host "  3. 确认有写入权限"
    exit 1
}

# 清理
Write-Host "[6/6] 清理临时文件..." -ForegroundColor Yellow
Set-Location $env:TEMP
Remove-Item -Recurse -Force $TempDir -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  同步完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "GitHub 仓库: https://github.com/$GitHubRepo"
Write-Host "Gitee 仓库:  https://gitee.com/$GiteeRepo"
Write-Host ""
Write-Host "后续同步: 推送至 GitHub 后会自动同步到 Gitee"
Write-Host ""

# 显示 Gitee 仓库信息
Write-Host "Gitee 仓库信息:" -ForegroundColor Cyan
Write-Host "  名称: awesome-kimi-skills"
Write-Host "  地址: https://gitee.com/$GiteeRepo"
Write-Host "  SSH:  git@gitee.com:$GiteeRepo.git"
Write-Host ""

Write-Host "✅ 初始化完成！" -ForegroundColor Green
