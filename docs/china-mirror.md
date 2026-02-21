# 国内镜像访问指南

> 为中国大陆用户提供更快的访问速度和更好的使用体验

---

## 🚀 国内镜像地址

由于网络原因，GitHub 在国内访问可能较慢。我们提供以下国内镜像：

### 主镜像（推荐）
- **Gitee**: https://gitee.com/godlike-kimi-skills/awesome-kimi-skills

### 备用镜像
- **GitCode**: https://gitcode.com/godlike-kimi-skills/awesome-kimi-skills
- **AtomGit**: https://atomgit.com/godlike-kimi-skills/awesome-kimi-skills

---

## 📥 快速安装命令（国内版）

### 方式一：使用 Gitee 镜像（推荐）

```bash
# 克隆仓库
git clone https://gitee.com/godlike-kimi-skills/awesome-kimi-skills.git

# 进入目录
cd awesome-kimi-skills

# 安装 Skill（示例：coding-agent）
cp -r skills/coding-agent ~/.kimi/skills/
```

### 方式二：一键安装脚本

```bash
# 下载安装脚本
curl -fsSL https://gitee.com/godlike-kimi-skills/awesome-kimi-skills/raw/main/scripts/install.sh | bash

# 或使用 wget
wget -qO- https://gitee.com/godlike-kimi-skills/awesome-kimi-skills/raw/main/scripts/install.sh | bash
```

### 方式三：批量安装

```bash
# 安装所有 Skills
for skill in awesome-kimi-skills/skills/*/; do
    cp -r "$skill" ~/.kimi/skills/
done
```

---

## 🔗 Gitee 访问链接

### 仓库页面
- **主仓库**: https://gitee.com/godlike-kimi-skills/awesome-kimi-skills
- **Issues**: https://gitee.com/godlike-kimi-skills/awesome-kimi-skills/issues
- **PR**: https://gitee.com/godlike-kimi-skills/awesome-kimi-skills/pulls

### 文档页面
- **使用指南**: https://gitee.com/godlike-kimi-skills/awesome-kimi-skills/blob/main/README.md
- **Skill 文档**: https://gitee.com/godlike-kimi-skills/awesome-kimi-skills/tree/main/skills

### 克隆地址
```bash
# HTTPS
https://gitee.com/godlike-kimi-skills/awesome-kimi-skills.git

# SSH
git@gitee.com:godlike-kimi-skills/awesome-kimi-skills.git
```

---

## ⚡ 速度对比

| 操作 | GitHub | Gitee | 速度提升 |
|------|--------|-------|----------|
| 克隆仓库 | 30-120s | 5-15s | **5-10x** |
| 拉取更新 | 10-30s | 2-5s | **5-6x** |
| 浏览文档 | 3-10s | 1-2s | **3-5x** |
| 下载文件 | 5-20s | 1-3s | **5-7x** |

> 数据基于中国大陆网络环境测试，实际速度可能因地区和网络而异。

---

## 🔄 同步频率

- **自动同步**: 每次 GitHub 推送后自动同步（约 1-2 分钟延迟）
- **手动同步**: 可通过 GitHub Actions 手动触发
- **同步状态**: 查看 [Actions 页面](https://github.com/godlike-kimi-skills/awesome-kimi-skills/actions)

---

## 📝 贡献代码

由于 Gitee 镜像为只读镜像，如需贡献代码：

1. **Fork 原仓库**: https://github.com/godlike-kimi-skills/awesome-kimi-skills
2. **在 GitHub 提交 PR**
3. **PR 合并后自动同步到 Gitee**

---

## ❓ 常见问题

### Q: Gitee 镜像和 GitHub 有什么区别？
A: 内容完全一致，Gitee 只是 GitHub 的镜像，每推送一次代码会自动同步。

### Q: 如何确保使用最新版本？
A: Gitee 镜像会在 GitHub 推送后 1-2 分钟内自动同步，几乎无延迟。

### Q: Gitee 镜像无法访问？
A: 可以尝试：
1. 检查网络连接
2. 使用备用镜像（GitCode）
3. 直接使用 GitHub 原站

### Q: 可以在 Gitee 提交 Issue 吗？
A: 建议统一在 [GitHub Issues](https://github.com/godlike-kimi-skills/awesome-kimi-skills/issues) 提交，方便管理和跟踪。

---

## 📞 联系我们

- **GitHub**: https://github.com/godlike-kimi-skills/awesome-kimi-skills
- **Gitee**: https://gitee.com/godlike-kimi-skills/awesome-kimi-skills
- **Issues**: https://github.com/godlike-kimi-skills/awesome-kimi-skills/issues

---

## ⚠️ 注意事项

1. **Gitee 镜像为只读**: 请勿直接向 Gitee 推送代码
2. **同步延迟**: 通常 1-2 分钟，极端情况下可能延迟
3. **访问限制**: Gitee 对匿名访问有限制，如遇限制请登录后访问

---

**推荐使用 Gitee 镜像以获得最佳体验！** 🚀
