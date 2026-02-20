# ArgoCD Skill

## 功能描述

ArgoCD GitOps管理工具，支持Application管理、Sync操作和仓库配置。

## Use When（触发条件）

- 需要创建、更新或删除ArgoCD Applications
- 执行Application同步（Sync）操作
- 管理Git仓库和Helm仓库配置
- 查看Application状态和同步历史
- 管理Projects和权限
- 查看和管理ArgoCD集群
- 处理Application自动同步配置
- 管理ArgoCD Secrets和凭据

## Out of Scope（边界）

- 不直接管理Kubernetes集群本身（仅通过ArgoCD操作）
- 不处理ArgoCD服务器的安装或升级
- 不管理ArgoCD的DEX/SSO认证配置
- 不提供ArgoCD服务器的高可用配置
- 不直接操作ArgoCD的数据库
- 不管理ArgoCD的通知配置（Notifications）
- 不提供ArgoCD的RBAC策略详细配置

## 核心功能

### 1. Application管理

```python
from main import ArgoCDSkill

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
    dest_server="https://kubernetes.default.svc",
    dest_namespace="default"
)

# 列出Applications
apps = skill.list_apps()
```

### 2. Sync操作

```python
# 同步Application
skill.sync_app("my-app", wait=True)

# 强制同步
skill.sync_app("my-app", force=True)

# 同步特定资源
skill.sync_app("my-app", resources=["Deployment/my-app"])
```

### 3. 仓库管理

```python
# 添加Git仓库
skill.add_repo(
    url="https://github.com/org/repo.git",
    username="git",
    password="token"
)

# 添加Helm仓库
skill.add_helm_repo(
    name="stable",
    url="https://charts.helm.sh/stable"
)

# 列出仓库
repos = skill.list_repos()
```

### 4. 状态查看

```python
# 获取Application详情
app_info = skill.get_app("my-app")

# 获取资源树
resources = skill.get_app_resources("my-app")

# 获取同步历史
history = skill.get_app_history("my-app")
```

## Application配置模板

### 基础Git应用

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/org/repo.git
    targetRevision: HEAD
    path: manifests
  destination:
    server: https://kubernetes.default.svc
    namespace: default
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

### Helm应用

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-helm-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://charts.helm.sh/stable
    targetRevision: 1.0.0
    chart: my-chart
    helm:
      values: |
        replicaCount: 2
        ingress:
          enabled: true
  destination:
    server: https://kubernetes.default.svc
    namespace: helm-apps
  syncPolicy:
    automated:
      prune: false
      selfHeal: true
```

### Kustomize应用

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-kustomize-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/org/repo.git
    targetRevision: HEAD
    path: overlays/production
    kustomize:
      namePrefix: prod-
  destination:
    server: https://kubernetes.default.svc
    namespace: production
```

## 配置参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `server` | str | Yes | ArgoCD服务器URL |
| `username` | str | No | ArgoCD用户名 |
| `password` | str | No | ArgoCD密码 |
| `token` | str | No | ArgoCD API Token |
| `insecure` | bool | No | 跳过TLS验证 |

## 返回值

标准响应对象：

```python
{
    "success": bool,
    "data": Any,
    "error": str | None
}
```

## 错误处理

```python
result = skill.sync_app("my-app")
if not result["success"]:
    print(f"Sync failed: {result['error']}")
```

## 依赖要求

- Python >= 3.8
- requests >= 2.28.0
- PyYAML >= 6.0

## 示例代码

见 `examples/` 目录。

## 测试

```bash
cd tests
pytest test_main.py -v
```

## 许可证

MIT License
