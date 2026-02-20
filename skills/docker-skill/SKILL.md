# Docker Skill

Docker容器管理工具，用于管理Docker容器、镜像、Compose编排等操作。

## 功能描述

提供完整的Docker容器生命周期管理功能，包括容器启停、镜像管理、日志查看和Docker Compose编排操作。Use when managing Docker containers, deploying containers, or when user mentions 'docker', 'container', 'docker-compose', '镜像'。

## 能力

- 容器管理：创建、启动、停止、重启、删除容器
- 镜像管理：拉取、构建、删除、查看镜像
- 日志查看：实时查看容器日志、历史日志检索
- Compose操作：编排多容器应用，支持启动、停止、重建
- 网络管理：创建和管理Docker网络
- 卷管理：持久化数据卷操作

## 用法

### 基本容器操作

```bash
# 列出所有容器
python main.py container ls --all

# 启动容器
python main.py container start my-container

# 停止容器
python main.py container stop my-container

# 重启容器
python main.py container restart my-container

# 删除容器
python main.py container rm my-container --force

# 查看容器日志
python main.py container logs my-container --tail 100 --follow

# 在容器中执行命令
python main.py container exec my-container "ls -la"
```

### 镜像管理

```bash
# 列出本地镜像
python main.py image ls

# 拉取镜像
python main.py image pull nginx:latest

# 构建镜像
python main.py image build -t myapp:1.0 -f Dockerfile .

# 删除镜像
python main.py image rm myapp:1.0

# 清理悬空镜像
python main.py image prune
```

### Docker Compose操作

```bash
# 启动所有服务
python main.py compose up -d

# 停止所有服务
python main.py compose down

# 重建并启动服务
python main.py compose up --build -d

# 查看Compose服务日志
python main.py compose logs --tail 50

# 扩展服务实例数
python main.py compose scale web=3 api=2
```

### 网络和卷管理

```bash
# 创建网络
python main.py network create my-network --driver bridge

# 列出网络
python main.py network ls

# 创建卷
python main.py volume create my-volume

# 列出卷
python main.py volume ls
```

## 参数说明

### 全局参数

- `--verbose`: 启用详细输出模式
- `--dry-run`: 仅显示将要执行的命令，不实际执行

### 容器操作参数

- `--all, -a`: 显示所有容器（包括停止的）
- `--force, -f`: 强制操作（如强制删除运行中的容器）
- `--tail`: 查看日志的最后N行
- `--follow, -f`: 实时跟踪日志输出
- `--name`: 指定容器名称
- `--port, -p`: 端口映射（格式：主机端口:容器端口）
- `--volume, -v`: 卷挂载（格式：主机路径:容器路径）
- `--env, -e`: 环境变量（格式：KEY=VALUE）

### 镜像操作参数

- `--tag, -t`: 镜像标签
- `--file, -f`: Dockerfile路径
- `--no-cache`: 构建时不使用缓存
- `--pull`: 始终拉取最新基础镜像

### Compose操作参数

- `--detach, -d`: 后台运行
- `--build`: 强制重新构建镜像
- `--remove-orphans`: 删除不再定义的服务容器
- `--file, -f`: 指定docker-compose.yml文件路径

## 环境要求

- Docker Engine >= 20.10
- Docker Compose >= 2.0
- Python >= 3.8
- 用户需有Docker操作权限（docker组或root）

## 注意事项

1. 部分操作需要管理员权限
2. 删除操作不可逆，请谨慎使用
3. 生产环境建议在操作前创建备份
4. 敏感信息（密码、密钥）建议使用环境变量或Docker Secrets

## 示例场景

### 部署Web应用

```bash
# 1. 拉取Nginx镜像
python main.py image pull nginx:alpine

# 2. 运行Nginx容器
python main.py container run nginx:alpine --name web-server -p 80:80 -d

# 3. 查看运行状态
python main.py container ls

# 4. 查看访问日志
python main.py container logs web-server --tail 20
```

### 使用Compose部署微服务

```bash
# 1. 在项目目录启动服务
python main.py compose up -d

# 2. 查看服务状态
python main.py compose ps

# 3. 重启特定服务
python main.py compose restart api-service

# 4. 查看所有服务日志
python main.py compose logs --tail 100
```
