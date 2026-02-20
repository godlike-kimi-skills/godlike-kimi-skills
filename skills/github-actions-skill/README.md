# GitHub Actions Skill

GitHub Actions CI/CD工作流管理工具，提供完整的DevOps自动化能力。

## 功能特性

- ✅ Workflow创建、编辑、删除
- ✅ 多种触发器配置（Push, PR, Schedule, Manual）
- ✅ Secrets和环境变量管理
- ✅ 工作流运行状态监控
- ✅ Self-hosted Runner管理
- ✅ 工作流模板生成

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 基础使用

```python
from main import GitHubActionsSkill

# 初始化
skill = GitHubActionsSkill(
    token="your-github-token",
    repo="owner/repository"
)

# 创建工作流
skill.create_workflow(
    name="ci-pipeline",
    triggers=["push", "pull_request"]
)

# 设置Secret
skill.set_secret("API_KEY", "your-secret")

# 查看运行状态
runs = skill.get_workflow_runs()
```

## 配置

| 环境变量 | 说明 | 必需 |
|---------|------|------|
| `GITHUB_TOKEN` | GitHub Personal Access Token | ✓ |
| `GITHUB_REPO` | 仓库名 (owner/repo) | ✓ |

## API文档

### 工作流管理

- `create_workflow(name, content, triggers, jobs)` - 创建工作流
- `delete_workflow(name)` - 删除工作流
- `get_workflow(name)` - 获取工作流内容
- `list_workflows()` - 列出所有工作流

### 触发器配置

- `configure_triggers(workflow_name, triggers)` - 配置触发器

### Secrets管理

- `set_secret(name, value)` - 设置Secret
- `delete_secret(name)` - 删除Secret
- `list_secrets()` - 列出所有Secrets

### 运行监控

- `get_workflow_runs()` - 获取运行记录
- `get_run_logs(run_id)` - 获取运行日志
- `rerun_workflow(run_id)` - 重新运行
- `cancel_workflow(run_id)` - 取消运行

### Runner管理

- `list_runners()` - 列出Self-hosted runners

## 示例

见 `examples/` 目录。

## 测试

```bash
pytest tests/ -v
```

## 许可证

MIT
