# GitLab CI Skill

GitLab CI/CD管理工具，支持`.gitlab-ci.yml`编辑、Runner管理和Pipeline监控。

## 功能特性

- ✅ `.gitlab-ci.yml`创建、编辑、验证
- ✅ GitLab Runner管理
- ✅ Pipeline查看和触发
- ✅ CI/CD变量管理
- ✅ Job日志获取
- ✅ CI配置模板生成

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 基础使用

```python
from main import GitLabCISkill

# 初始化
skill = GitLabCISkill(
    token="your-gitlab-token",
    project="group/project"
)

# 创建CI配置
skill.create_ci_config(
    stages=["build", "test", "deploy"],
    jobs={
        "test": {
            "stage": "test",
            "script": ["pytest"]
        }
    }
)

# 触发Pipeline
skill.trigger_pipeline(ref="main")

# 查看Pipeline状态
pipelines = skill.list_pipelines()
```

## 配置

| 环境变量 | 说明 | 必需 |
|---------|------|------|
| `GITLAB_TOKEN` | GitLab Personal Access Token | ✓ |
| `GITLAB_PROJECT` | 项目路径 (group/project) | ✓ |

## API文档

### CI配置管理

- `get_ci_config(ref)` - 获取CI配置
- `create_ci_config(stages, jobs, variables, ref)` - 创建CI配置
- `update_ci_job(job_name, job_config, ref)` - 更新Job
- `validate_ci_config(content)` - 验证配置

### Runner管理

- `list_runners(scope)` - 列出Runners
- `get_runner(runner_id)` - 获取Runner详情
- `register_runner(token, description, tags)` - 注册Runner
- `unregister_runner(runner_id)` - 注销Runner

### Pipeline管理

- `list_pipelines(status, ref, limit)` - 列出Pipelines
- `get_pipeline(pipeline_id)` - 获取Pipeline详情
- `trigger_pipeline(ref, variables)` - 触发Pipeline
- `retry_pipeline(pipeline_id)` - 重试Pipeline
- `cancel_pipeline(pipeline_id)` - 取消Pipeline

### 变量管理

- `list_variables()` - 列出变量
- `set_variable(key, value, protected, masked)` - 设置变量
- `delete_variable(key)` - 删除变量

### 模板

- `generate_ci_template(template_type, stages)` - 生成CI模板

## 示例

见 `examples/` 目录。

## 测试

```bash
pytest tests/ -v
```

## 许可证

MIT
