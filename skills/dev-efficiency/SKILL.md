# Dev Efficiency

**开发效率工具集** - 基于 Oh My Zsh 和 Powerlevel10k

开发者生产力提升工具，快捷键、别名、自动化。

---

## 核心特性

### ⚡ 效率工具

| 工具 | 说明 |
|------|------|
| **快捷别名** | 常用命令缩写 |
| **模板生成** | 项目脚手架 |
| **Git快捷** | 简化Git操作 |
| **智能补全** | 命令自动补全 |

### 🛠️ 内置功能

```bash
# 快捷命令
g s  → git status
g c  → git commit
g p  → git push

# 项目模板
dev-efficiency init python-project
dev-efficiency init node-project
```

---

## 使用方法

### 安装别名
```bash
dev-efficiency install-aliases --shell powershell
```

### 生成项目模板
```bash
dev-efficiency init --template python --name my-project
```

### 效率统计
```bash
dev-efficiency stats --days 7
```

---

## 参考实现

- **Oh My Zsh**: Zsh 配置框架
- **Powerlevel10k**: Zsh 主题
- **Starship**: 跨 Shell 提示符

---

## 版本信息

- **Version**: 1.0.0
- **Author**: KbotGenesis
