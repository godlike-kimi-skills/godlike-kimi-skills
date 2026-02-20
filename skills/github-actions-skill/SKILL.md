# GitHub Actions Skill

## 功能描述

GitHub Actions工作流管理工具，提供完整的CI/CD工作流自动化能力。

## Use When（触发条件）

- 需要创建、编辑或管理GitHub Actions工作流
- 配置CI/CD流水线（构建、测试、部署）
- 管理GitHub Secrets和环境变量
- 设置工作流触发器（push, pull_request, schedule等）
- 查看工作流运行状态和日志
- 管理Self-hosted runners
- 需要复用或分享GitHub Actions工作流

## Out of Scope（边界）

- 不管理GitHub仓库源代码本身
- 不处理GitHub Issues或Pull Requests的代码审查
- 不直接操作GitHub仓库的分支管理（除工作流相关外）
- 不管理GitHub Packages的权限设置
- 不提供GitHub Enterprise Server的专属功能
- 不处理非Actions相关的GitHub API操作

## 核心功能

### 1. Workflow创建与管理

```python
from main import GitHubActionsSkill

skill = GitHubActionsSkill()

# 创建新工作流
workflow = skill.create_workflow(
    name="ci-pipeline",
    triggers=["push", "pull_request"],
    jobs=["build", "test", "deploy"]
)
```

### 2. 触发器配置

```python
# 配置多种触发器
triggers = skill.configure_triggers({
    "push": {"branches": ["main", "develop"]},
    "pull_request": {"branches": ["main"]},
    "schedule": [{"cron": "0 2 * * *"}],
    "workflow_dispatch": {}
})
```

### 3. Secrets管理

```python
# 管理仓库Secrets
skill.set_secret("API_KEY", "secret-value")
skill.set_secret("DATABASE_URL", "postgres://localhost/db")
secrets = skill.list_secrets()
```

### 4. 工作流运行监控

```python
# 获取工作流运行状态
runs = skill.get_workflow_runs("ci-pipeline")
logs = skill.get_run_logs(run_id=12345)
skill.rerun_workflow(run_id=12345)
```

### 5. Runner管理

```python
# 管理Self-hosted runners
runners = skill.list_runners()
skill.register_runner("my-runner", labels=["linux", "gpu"])
skill.remove_runner("runner-id")
```

## 工作流模板

### 基础CI模板

```yaml
name: CI Pipeline
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm run build
```

### 多环境部署模板

```yaml
name: Deploy
on:
  push:
    tags: ['v*']

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4
      - run: ./deploy.sh staging
  
  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    steps:
      - run: ./deploy.sh production
```

## 配置参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `token` | str | Yes | GitHub Personal Access Token |
| `repo` | str | Yes | 仓库名 (owner/repo) |
| `base_url` | str | No | GitHub API URL (默认: https://api.github.com) |

## 返回值

所有方法返回标准响应对象：

```python
{
    "success": bool,
    "data": Any,
    "error": str | None
}
```

## 错误处理

```python
result = skill.create_workflow(name="test")
if not result["success"]:
    print(f"Error: {result['error']}")
```

## 依赖要求

- Python >= 3.8
- PyGithub >= 2.1.0
- PyYAML >= 6.0

## 示例代码

见 `examples/` 目录：
- `example_basic.py` - 基础使用示例
- `example_advanced.py` - 高级功能示例

## 测试

```bash
cd tests
pytest test_main.py -v
```

## 许可证

MIT License
