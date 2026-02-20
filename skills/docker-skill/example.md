# Docker Skill 使用示例

## 示例1：快速部署Nginx服务

```bash
# 拉取最新Nginx镜像
python main.py image pull nginx:latest

# 运行Nginx容器，映射80端口
python main.py container run nginx:latest --name my-nginx -p 8080:80 -d

# 验证容器运行状态
python main.py container ls

# 查看容器日志
python main.py container logs my-nginx --tail 50
```

## 示例2：构建并运行自定义应用

```bash
# 在项目目录构建镜像（假设有Dockerfile）
python main.py image build -t my-python-app:1.0 .

# 运行应用容器，挂载本地目录
python main.py container run my-python-app:1.0 \
  --name python-app \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -e DEBUG=true \
  -d

# 进入容器调试
python main.py container exec python-app "/bin/bash"
```

## 示例3：Docker Compose多服务部署

假设项目目录有以下 `docker-compose.yml`：

```yaml
version: '3.8'
services:
  web:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./html:/usr/share/nginx/html
  
  api:
    build: ./api
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
  
  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secretpass
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

操作命令：

```bash
# 启动所有服务（后台运行）
python main.py compose up -d

# 查看服务状态
python main.py compose ps

# 查看web服务日志
python main.py compose logs web -f

# 重启api服务
python main.py compose restart api

# 停止并删除所有服务
python main.py compose down --volumes
```

## 示例4：容器管理和清理

```bash
# 列出所有运行中的容器
python main.py container ls

# 列出所有容器（包括已停止）
python main.py container ls --all

# 停止多个容器
python main.py container stop container1 container2 container3

# 删除所有已停止的容器
python main.py container prune

# 清理悬空镜像
python main.py image prune

# 全面清理（容器、镜像、卷、网络）
python main.py system prune --all --volumes
```

## 示例5：网络和数据卷管理

```bash
# 创建自定义网络
python main.py network create my-app-network --driver bridge

# 创建数据卷
python main.py volume create app-data

# 运行容器连接到自定义网络
python main.py container run nginx:alpine \
  --name web-server \
  --network my-app-network \
  -v app-data:/data \
  -d

# 查看网络详情
python main.py network inspect my-app-network

# 查看卷详情
python main.py volume inspect app-data
```

## 示例6：故障排查

```bash
# 查看容器详细信息
python main.py container inspect my-container

# 查看容器资源使用情况
python main.py container stats my-container

# 实时跟踪容器日志
python main.py container logs my-container --follow --tail 10

# 复制文件从容器到主机
python main.py container cp my-container:/app/logs/error.log ./error.log

# 查看容器进程
python main.py container top my-container
```
