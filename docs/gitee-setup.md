# Gitee 国内镜像配置指南

> 本指南详细说明如何为 Awesome Kimi Skills 项目配置 Gitee 国内镜像

---

## 📋 目录

1. [Gitee 注册步骤](#1-gitee-注册步骤)
2. [创建组织步骤](#2-创建组织步骤)
3. [配置 SSH Key](#3-配置-ssh-key)
4. [设置自动同步](#4-设置自动同步)
5. [故障排除](#5-故障排除)

---

## 1. Gitee 注册步骤

### 1.1 访问 Gitee 官网
- 打开浏览器访问：https://gitee.com
- 点击右上角「注册」按钮

### 1.2 填写注册信息
```
用户名: godlike-kimi-skills  （建议与 GitHub 组织名保持一致）
邮箱: 你的邮箱地址
密码: 强密码（建议16位以上，包含大小写字母、数字、特殊符号）
```

### 1.3 邮箱验证
- 登录注册邮箱
- 查收 Gitee 验证邮件
- 点击验证链接完成注册

### 1.4 实名认证（推荐）
- 进入「设置」→「实名认证」
- 完成实名认证后可享受更多功能

---

## 2. 创建组织步骤

### 2.1 创建组织
1. 登录 Gitee 后，点击右上角 `+` 号
2. 选择「创建组织」
3. 填写组织信息：
   - 组织名称: `godlike-kimi-skills`
   - 组织路径: `godlike-kimi-skills`
   - 描述: `Awesome Kimi Skills - 最全、最快、最强的 Kimi Code CLI Skills 集合`
   - 可见性: 公开

### 2.2 创建仓库
1. 进入组织页面
2. 点击「创建仓库」
3. 填写仓库信息：
   - 仓库名称: `awesome-kimi-skills`
   - 仓库描述: `Kimi Code CLI Skills 集合 - 国内镜像`
   - 可见性: 公开
   - 初始化: 不初始化（空仓库，等待 GitHub 同步）

---

## 3. 配置 SSH Key

### 3.1 生成 SSH Key（本地操作）
```bash
# 生成新的 SSH Key
ssh-keygen -t ed25519 -C "gitee-sync@awesome-kimi-skills" -f ~/.ssh/gitee_sync

# 查看公钥
cat ~/.ssh/gitee_sync.pub
```

### 3.2 在 Gitee 添加公钥
1. 登录 Gitee
2. 点击头像 → 「设置」
3. 左侧菜单选择「SSH 公钥」
4. 点击「添加公钥」
5. 填写信息：
   - 标题: `GitHub Actions Sync`
   - 公钥: 粘贴上面生成的公钥内容
   - 类型: 部署公钥（只读）或 个人公钥（推荐）

### 3.3 在 GitHub 添加私钥
1. 打开 GitHub 仓库页面
2. 进入 Settings → Secrets and variables → Actions
3. 点击「New repository secret」
4. 添加 Secret：
   - Name: `GITEE_PRIVATE_KEY`
   - Value: 粘贴私钥内容（`~/.ssh/gitee_sync` 文件内容）

```bash
# 查看私钥（用于复制到 GitHub Secrets）
cat ~/.ssh/gitee_sync
```

---

## 4. 设置自动同步

### 4.1 确认 Workflow 文件

确保 `.github/workflows/sync-to-gitee.yml` 存在：

```yaml
name: Sync to Gitee

on:
  push:
    branches: [main, master]
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout source
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Sync to Gitee
        uses: wearerequired/git-mirror-action@master
        env:
          SSH_PRIVATE_KEY: ${{ secrets.GITEE_PRIVATE_KEY }}
        with:
          source-repo: 'git@github.com:godlike-kimi-skills/awesome-kimi-skills.git'
          destination-repo: 'git@gitee.com:godlike-kimi-skills/awesome-kimi-skills.git'
```

### 4.2 测试同步
1. 推送一个测试提交到 GitHub main 分支
2. 查看 GitHub Actions 是否正常运行
3. 检查 Gitee 仓库是否收到同步

### 4.3 手动触发同步
在 GitHub 仓库页面：
1. 进入 Actions 标签
2. 选择 "Sync to Gitee" workflow
3. 点击 "Run workflow" → "Run workflow"

---

## 5. 故障排除

### 5.1 同步失败：权限错误
```
Error: Permission denied (publickey)
```
**解决方案：**
- 检查 Gitee 是否添加了正确的公钥
- 检查 GitHub Secrets 中的 `GITEE_PRIVATE_KEY` 是否正确
- 确认密钥对匹配

### 5.2 同步失败：仓库不存在
```
Error: repository not found
```
**解决方案：**
- 在 Gitee 创建同名仓库
- 确认仓库路径正确

### 5.3 同步失败：分支保护
```
Error: failed to push some refs
```
**解决方案：**
- 检查 Gitee 仓库的分支保护设置
- 确认部署密钥有写入权限

### 5.4 网络超时
```
Error: Connection timed out
```
**解决方案：**
- 重新运行 workflow
- 检查 GitHub Actions 状态页面

---

## 📚 相关链接

- [Gitee 官网](https://gitee.com)
- [Gitee 帮助文档](https://gitee.com/help)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [awesome-kimi-skills Gitee 镜像](https://gitee.com/godlike-kimi-skills/awesome-kimi-skills)

---

## ✅ 检查清单

- [ ] Gitee 账号注册完成
- [ ] 组织 `godlike-kimi-skills` 创建完成
- [ ] 仓库 `awesome-kimi-skills` 创建完成
- [ ] SSH Key 生成完成
- [ ] Gitee 公钥添加完成
- [ ] GitHub Secrets 私钥添加完成
- [ ] 自动同步测试成功

---

**配置完成！** 🎉

现在每次推送到 GitHub 都会自动同步到 Gitee，为国内用户提供更快的访问速度。
