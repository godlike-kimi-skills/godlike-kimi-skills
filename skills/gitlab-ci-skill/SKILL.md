# GitLab CI Skill

## 功能描述

GitLab CI/CD管理工具，支持`.gitlab-ci.yml`编辑、Runner管理和Pipeline监控。

## Use When（触发条件）

- 需要创建、编辑或管理`.gitlab-ci.yml`文件
- 配置GitLab CI/CD Pipeline
- 管理GitLab Runners（注册、查看状态）
- 查看Pipeline执行状态和日志
- 触发手动Pipeline执行
- 管理CI/CD变量和Secrets
- 配置CI/CD调度（Schedules）
- 查看CI/CD作业（Jobs）详情

## Out of Scope（边界）

- 不管理GitLab仓库源代码本身（除CI配置文件外）
- 不处理GitLab Issues或Merge Requests的代码审查
- 不管理GitLab项目的常规设置（仅CI/CD相关）
- 不直接操作GitLab Runner的操作系统
- 不提供GitLab Self-Managed的专属系统级配置
- 不管理GitLab的LDAP或其他认证集成
- 不处理GitLab Pages的非CI相关配置

## 核心功能

### 1. `.gitlab-ci.yml`管理

```python
from main import GitLabCISkill

skill = GitLabCISkill(token="your-token", project="group/project")

# 创建CI配置
skill.create_ci_config(
    stages=["build", "test", "deploy"],
    jobs={
        "build": {
            "stage": "build",
            "script": ["make build"],
            "tags": ["docker"]
        }
    }
)

# 编辑现有配置
skill.update_ci_job("test", {
    "script": ["pytest", "coverage report"],
    "artifacts": {"reports": {"coverage_report": {"coverage_format": "cobertura", "path": "coverage.xml"}}}
})
```

### 2. Runner管理

```python
# 列出项目Runners
runners = skill.list_runners()

# 注册新Runner
skill.register_runner(
    token="registration-token",
    description="docker-runner",
    tags=["docker", "linux"]
)

# 获取Runner详情
runner_info = skill.get_runner(runner_id=42)
```

### 3. Pipeline管理

```python
# 列出Pipelines
pipelines = skill.list_pipelines(status="success")

# 获取Pipeline详情
pipeline = skill.get_pipeline(pipeline_id=123)

# 触发Pipeline
skill.trigger_pipeline(ref="main", variables={"DEPLOY_ENV": "staging"})

# 重试失败的Jobs
skill.retry_pipeline(pipeline_id=123)
```

### 4. CI/CD变量管理

```python
# 设置变量
skill.set_variable("API_KEY", "secret-value", protected=True, masked=True)

# 列出变量
variables = skill.list_variables()

# 删除变量
skill.delete_variable("OLD_VAR")
```

## CI配置模板

### 基础模板

```yaml
stages:
  - build
  - test
  - deploy

variables:
  NODE_VERSION: "20"

cache:
  paths:
    - node_modules/

build:
  stage: build
  image: node:${NODE_VERSION}
  script:
    - npm ci
    - npm run build
  artifacts:
    paths:
      - dist/

test:
  stage: test
  image: node:${NODE_VERSION}
  script:
    - npm test
  coverage: '/All files[^|]*\|[^|]*\s+([\d\.]+)/'

deploy:
  stage: deploy
  script:
    - echo "Deploying..."
  environment:
    name: production
  only:
    - main
```

### 多环境部署模板

```yaml
stages:
  - build
  - deploy_staging
  - deploy_production

build:
  stage: build
  script:
    - ./build.sh

deploy_staging:
  stage: deploy_staging
  script:
    - ./deploy.sh staging
  environment:
    name: staging
    url: https://staging.example.com
  only:
    - develop

deploy_production:
  stage: deploy_production
  script:
    - ./deploy.sh production
  environment:
    name: production
    url: https://example.com
  when: manual
  only:
    - main
```

## 配置参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `token` | str | Yes | GitLab Personal Access Token |
| `project` | str | Yes | 项目路径 (group/project) 或项目ID |
| `url` | str | No | GitLab URL (默认: https://gitlab.com) |
| `timeout` | int | No | 请求超时(秒) |

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
result = skill.create_ci_config(stages=["build"])
if not result["success"]:
    print(f"Error: {result['error']}")
```

## 依赖要求

- Python >= 3.8
- python-gitlab >= 4.0.0
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
