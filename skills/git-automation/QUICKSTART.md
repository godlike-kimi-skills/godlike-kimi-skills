# Kbot Git 自动化系统 - 快速入门

## 系统搭建完成！

你的全自动化 Git + GitHub + 容灾备份系统已就绪。

---

## 功能清单

| 功能 | 状态 | 命令 |
|------|------|------|
| 自动建仓 | ✅ | `kbot-init <name>` |
| Git 版本管理 | ✅ | `kbot-backup [msg]` |
| GitHub 集成 | ✅ | 自动创建私有仓库 |
| 容灾备份 | ✅ | 自动标签 + 快照 |
| 一键恢复 | ✅ | `kbot-restore [options]` |
| Git Hooks | ✅ | pre-commit, post-commit |
| 定时备份 | ✅ | GitHub Actions 模板 |

---

## 演示工作流

### 场景：开发一个新项目

```powershell
# Step 1: 创建新项目（自动建仓）
> kbot-init my-awesome-app -Description "我的新项目"

🚀 Kbot Git 初始化系统
========================================
✅ Git 初始化完成
✅ 创建 .gitignore
✅ 创建 README.md
📦 创建 GitHub 仓库...
✅ GitHub 仓库创建并推送成功
========================================
🎉 项目初始化完成！
========================================
📁 本地路径: C:\Users\wang-\my-awesome-app
🌐 GitHub: https://github.com/你的用户名/my-awesome-app
```

```powershell
# Step 2: 开发代码
# ... 修改代码 ...

# Step 3: 自动备份
> kbot-backup "完成了用户登录功能"

💾 Kbot Git 备份系统
========================================
✅ 暂存所有更改
✅ 提交成功: 完成了用户登录功能
📤 推送到远程...
✅ 创建标签: backup-20240118-143022
========================================
🎉 备份完成！
========================================
```

```powershell
# Step 4: 出错了！恢复！
# 不小心删除了重要文件...

> kbot-restore --list

⏰ Kbot Git 恢复系统
========================================
📋 可用备份列表:
--------------------
  [1] backup-20240118-143022
      Commit: abc1234 | 2 minutes ago
      Message: 完成了用户登录功能

  [2] backup-20240118-142500
      Commit: def5678 | 1 hour ago
      Message: Initial commit
```

```powershell
# 恢复到5分钟前
> kbot-restore --timeago 5m

🎯 恢复目标: 提交: abc1234
📋 恢复内容预览:
  abc1234 完成了用户登录功能
========================================
⚠️  高危操作警告
========================================
此操作将:
  1. 创建当前状态的快照
  2. 重置工作目录到目标版本
📸 创建当前状态快照: pre-restore-20240118-143100
确认恢复? 输入 'yes' 继续: yes

🔄 正在恢复...
========================================
🎉 恢复完成！
========================================
📌 原分支: main
🆕 恢复分支: restored-20240118-143100
🔖 恢复点: abc1234
```

---

## 常用命令速查

```bash
# 创建新项目
kbot-init <project-name> [-Description "描述"] [-IsPrivate $true]

# 备份当前更改
kbot-backup ["提交消息"]

# 查看所有备份
kbot-restore --list

# 恢复到指定标签
kbot-restore --tag backup-xxx

# 恢复到指定提交
kbot-restore --commit abc1234

# 恢复到N小时/天前
kbot-restore --timeago 1h    # 1小时前
kbot-restore --timeago 1d    # 1天前

# 交互式选择恢复
kbot-restore --interactive
```

---

## 自动触发规则

Kbot 会自动在以下场景执行操作：

1. **检测新项目**
   - 当你说"帮我做一个..."时，自动提示初始化

2. **自动备份**
   - 修改文件后自动提示备份
   - 提交前自动创建快照标签
   - 提交后自动推送到 GitHub

3. **容灾恢复**
   - 执行危险命令（如删除文件）前自动备份
   - 出错时提示恢复到上一版本

4. **定时备份**
   - 每小时自动检查并备份（需启用 GitHub Actions）

---

## 下一步

1. **登录 GitHub**
   ```powershell
   gh auth login
   ```

2. **创建测试项目**
   ```powershell
   kbot-init test-project
   ```

3. **体验完整流程**
   - 修改文件
   - 运行 kbot-backup
   - 删除文件
   - 运行 kbot-restore

---

## 文件位置

```
~/.kimi/scripts/git-automation/
├── Kbot_Git_Init.ps1      # 项目初始化
├── Kbot_Git_Backup.ps1    # 备份脚本
├── Kbot_Git_Restore.ps1   # 恢复脚本
├── install-hooks.ps1      # 安装 hooks
└── setup-aliases.ps1      # 设置别名

~/.kimi/skills/git-automation/
├── SKILL.md               # Kbot 技能定义
└── QUICKSTART.md          # 本文件

~/.kimi/templates/github-workflows/
└── kbot-auto-backup.yml   # GitHub Actions 模板
```

---

**系统已就绪，开始你的第一个项目吧！** 🚀
