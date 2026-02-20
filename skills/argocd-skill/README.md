# ArgoCD Skill

ArgoCD GitOps管理工具，支持Application管理、Sync操作和仓库配置。

## 功能特性

- ✅ Application创建、更新、删除
- ✅ 同步操作（Sync、强制同步、回滚）
- ✅ Git/Helm仓库管理
- ✅ Application状态监控
- ✅ 资源树查看
- ✅ 同步历史管理
- ✅ Application模板生成

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 基础使用

```python
from main import ArgoCDSkill

# 初始化
skill = ArgoCDSkill(
    server="https://argocd.example.com",
    username="admin",
    password="password"
)

# 创建Application
skill.create_app(
    name="my-app",
    repo_url="https://github.com/org/repo.git",
    path="manifests",
    dest_namespace="default"
)

# 同步Application
skill.sync_app("my-app", wait=True)

# 查看Application状态
app_info = skill.get_app("my-app")
```

## 配置

| 环境变量 | 说明 | 必需 |
|---------|------|------|
| `ARGOCD_SERVER` | ArgoCD服务器URL | ✓ |
| `ARGOCD_TOKEN` | ArgoCD API Token | 与username/password二选一 |
| `ARGOCD_USERNAME` | ArgoCD用户名 | 与token二选一 |
| `ARGOCD_PASSWORD` | ArgoCD密码 | 与token二选一 |

## API文档

### Application管理

- `create_app(name, repo_url, path, ...)` - 创建Application
- `delete_app(name, cascade)` - 删除Application
- `get_app(name)` - 获取Application详情
- `list_apps(project)` - 列出Applications

### 同步操作

- `sync_app(name, revision, resources, prune, force, wait)` - 同步Application
- `rollback_app(name, history_id)` - 回滚Application

### 资源管理

- `get_app_resources(name)` - 获取资源树
- `get_app_history(name, limit)` - 获取同步历史

### 仓库管理

- `add_repo(url, username, password)` - 添加Git仓库
- `delete_repo(url)` - 删除仓库
- `list_repos()` - 列出仓库
- `add_helm_repo(name, url)` - 添加Helm仓库

### 项目管理

- `list_projects()` - 列出ArgoCD项目

### 模板

- `generate_app_template(app_type, **kwargs)` - 生成Application模板

## 示例

见 `examples/` 目录。

## 测试

```bash
pytest tests/ -v
```

## 许可证

MIT
