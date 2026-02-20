# Init Script Generator

**初始化脚本生成器** - 项目启动配置自动化

一键生成项目初始化脚本、环境配置、依赖安装。

---

## 核心特性

### 🚀 初始化模板

| 项目类型 | 包含内容 |
|---------|---------|
| **Python** | venv、requirements、pytest |
| **Node.js** | package.json、eslint、prettier |
| **Go** | go.mod、Makefile、Dockerfile |
| **Rust** | Cargo.toml、rustfmt、clippy |

### 📦 生成内容

- 项目结构
- 配置文件
- CI/CD脚本
- Docker配置

---

## 使用方法

### 生成Python项目
```bash
init-script-generator python --name my-project --features "lint,test,docs"
```

### 生成Node项目
```bash
init-script-generator node --name my-app --type "typescript"
```

### 生成配置
```bash
init-script-generator docker --base python:3.12
```

---

## 参考实现

- **Cookiecutter**: 项目模板工具
- **Yeoman**: 项目脚手架

---

## 版本信息

- **Version**: 1.0.0
- **Author**: KbotGenesis
