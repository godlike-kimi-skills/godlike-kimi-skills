# Jenkins Skill

## 功能描述

Jenkins流水线管理工具，支持Job创建、Build触发和Pipeline配置。

## Use When（触发条件）

- 需要创建、配置或管理Jenkins Job
- 触发Jenkins Build并监控执行状态
- 配置Jenkins Pipeline（声明式或脚本式）
- 管理Jenkins节点和Executor
- 查看Build日志和测试结果
- 配置Jenkins凭据（Credentials）
- 管理Jenkins插件
- 需要自动化Jenkins操作

## Out of Scope（边界）

- 不直接管理Jenkins服务器安装或升级
- 不处理Jenkins系统级的安全配置（如安全 realm）
- 不提供Jenkins UI的主题定制
- 不直接操作Jenkins底层文件系统
- 不管理Jenkins备份策略（仅触发备份Job）
- 不提供Slave节点的操作系统级管理
- 不处理非Pipeline类型的Freestyle Job详细配置

## 核心功能

### 1. Job创建与管理

```python
from main import JenkinsSkill

skill = JenkinsSkill(url="http://jenkins.example.com", 
                     username="admin", 
                     token="api-token")

# 创建Pipeline Job
skill.create_job(
    name="my-pipeline",
    job_type="pipeline",
    config={
        "script": "pipeline { agent any; stages { stage('Build') { steps { sh 'make' } } } }"
    }
)
```

### 2. Build触发与监控

```python
# 触发Build
result = skill.trigger_build("my-pipeline", parameters={"BRANCH": "main"})

# 等待Build完成
skill.wait_for_build("my-pipeline", build_number=result["data"]["number"])

# 获取Build日志
logs = skill.get_build_logs("my-pipeline", build_number=123)
```

### 3. Pipeline配置

```python
# 使用声明式Pipeline
pipeline_script = """
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        stage('Test') {
            steps {
                sh 'mvn test'
            }
        }
    }
}
"""

skill.update_job_config("my-pipeline", {"script": pipeline_script})
```

### 4. 节点管理

```python
# 列出所有节点
nodes = skill.list_nodes()

# 获取节点信息
node_info = skill.get_node("agent-1")
```

### 5. 凭据管理

```python
# 创建凭据
skill.create_credential(
    id="docker-hub",
    credential_type="username_password",
    username="dockeruser",
    password="dockerpass"
)
```

## Pipeline模板

### 基础CI模板

```groovy
pipeline {
    agent any
    
    environment {
        NODE_ENV = 'production'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Install') {
            steps {
                sh 'npm ci'
            }
        }
        
        stage('Build') {
            steps {
                sh 'npm run build'
            }
        }
        
        stage('Test') {
            steps {
                sh 'npm test'
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
    }
}
```

### 多分支Pipeline

```groovy
multibranchPipelineJob('my-project') {
    branchSources {
        git {
            id('origin')
            remote('https://github.com/user/repo.git')
            credentialsId('github-token')
        }
    }
}
```

## 配置参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| `url` | str | Yes | Jenkins URL |
| `username` | str | Yes | Jenkins用户名 |
| `token` | str | Yes | Jenkins API Token |
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
result = skill.trigger_build("my-job")
if not result["success"]:
    print(f"Build failed: {result['error']}")
```

## 依赖要求

- Python >= 3.8
- python-jenkins >= 1.8.0
- requests >= 2.28.0

## 示例代码

见 `examples/` 目录。

## 测试

```bash
cd tests
pytest test_main.py -v
```

## 许可证

MIT License
