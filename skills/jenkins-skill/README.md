# Jenkins Skill

Jenkins流水线管理工具，支持Job创建、Build触发和Pipeline配置。

## 功能特性

- ✅ Job创建、配置、删除
- ✅ Build触发和状态监控
- ✅ Pipeline脚本配置（声明式/脚本式）
- ✅ 节点管理
- ✅ 构建队列查看
- ✅ Build日志获取
- ✅ Pipeline模板生成

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 基础使用

```python
from main import JenkinsSkill

# 初始化
skill = JenkinsSkill(
    url="http://jenkins.example.com",
    username="admin",
    token="api-token"
)

# 创建Job
skill.create_job(
    name="my-pipeline",
    job_type="pipeline",
    config={"script": "pipeline { agent any; stages { stage('Build') { steps { echo 'Building...' } } } }"}
)

# 触发Build
skill.trigger_build("my-pipeline")

# 查看Build状态
builds = skill.list_builds("my-pipeline")
```

## 配置

| 环境变量 | 说明 | 必需 |
|---------|------|------|
| `JENKINS_URL` | Jenkins URL | ✓ |
| `JENKINS_USER` | Jenkins用户名 | ✓ |
| `JENKINS_TOKEN` | Jenkins API Token | ✓ |

## API文档

### Job管理

- `create_job(name, job_type, config)` - 创建Job
- `delete_job(name)` - 删除Job
- `get_job_info(name)` - 获取Job信息
- `list_jobs()` - 列出所有Jobs
- `update_job_config(name, config)` - 更新Job配置

### Build管理

- `trigger_build(name, parameters, block)` - 触发Build
- `get_build_info(job_name, build_number)` - 获取Build信息
- `get_build_logs(job_name, build_number)` - 获取Build日志
- `stop_build(job_name, build_number)` - 停止Build
- `list_builds(job_name, limit)` - 列出Build历史

### 节点管理

- `list_nodes()` - 列出所有节点

### 队列管理

- `get_queue()` - 获取构建队列

### 模板

- `generate_pipeline_template(template_type, language)` - 生成Pipeline模板

## 示例

见 `examples/` 目录。

## 测试

```bash
pytest tests/ -v
```

## 许可证

MIT
