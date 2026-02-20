# Kubernetes Skill

Kubernetes集群管理工具，用于管理Pod、Deployment、Service等资源。

## 功能描述

提供完整的Kubernetes集群管理功能，包括Pod/Deployment/Service管理、日志查看和扩缩容操作。Use when managing Kubernetes clusters, deploying applications to K8s, or when user mentions 'kubernetes', 'k8s', 'kubectl', 'pod', 'deployment'。

## 能力

- 资源管理：管理Pod、Deployment、Service、ConfigMap、Secret
- 集群信息：查看节点状态、集群事件、资源使用情况
- 日志和调试：查看Pod日志、进入容器执行命令、端口转发
- 扩缩容：Deployment/StatefulSet水平扩缩容
- 配置管理：应用YAML配置、管理ConfigMap和Secret
- 命名空间：多命名空间资源管理

## 用法

### 集群信息查看

```bash
# 查看集群信息
python main.py cluster info

# 查看节点状态
python main.py node ls

# 查看节点详情
python main.py node describe <node-name>
```

### Pod管理

```bash
# 列出所有Pod
python main.py pod ls

# 列出特定命名空间的Pod
python main.py pod ls -n kube-system

# 查看Pod详情
python main.py pod describe <pod-name>

# 查看Pod日志
python main.py pod logs <pod-name> --tail 100

# 实时跟踪Pod日志
python main.py pod logs <pod-name> -f

# 在Pod中执行命令
python main.py pod exec <pod-name> -- "ls -la"

# 进入Pod交互式shell
python main.py pod exec <pod-name> -it -- /bin/bash

# 删除Pod
python main.py pod delete <pod-name>

# 端口转发
python main.py pod port-forward <pod-name> 8080:80
```

### Deployment管理

```bash
# 列出所有Deployment
python main.py deployment ls

# 创建Deployment
python main.py deployment create my-deployment --image nginx:1.20 --replicas 3

# 更新Deployment镜像
python main.py deployment set-image my-deployment nginx=nginx:1.21

# 水平扩缩容
python main.py deployment scale my-deployment --replicas 5

# 查看Deployment滚动状态
python main.py deployment rollout-status my-deployment

# 回滚Deployment
python main.py deployment rollout-undo my-deployment

# 删除Deployment
python main.py deployment delete my-deployment
```

### Service管理

```bash
# 列出所有Service
python main.py service ls

# 查看Service详情
python main.py service describe <service-name>

# 创建NodePort服务
python main.py service create my-service --type NodePort --port 80 --target-port 8080

# 暴露Deployment为Service
python main.py service expose deployment my-deployment --port 80 --target-port 8080

# 删除Service
python main.py service delete my-service
```

### 配置和Secret管理

```bash
# 列出ConfigMaps
python main.py configmap ls

# 创建ConfigMap
python main.py configmap create my-config --from-file=config.json

# 列出Secrets
python main.py secret ls

# 创建Secret
python main.py secret create my-secret --from-literal=password=secret123
```

### 应用YAML配置

```bash
# 应用YAML文件
python main.py apply -f deployment.yaml

# 应用整个目录
python main.py apply -f ./k8s-manifests/

# 预览变更（dry-run）
python main.py apply -f deployment.yaml --dry-run

# 删除资源
python main.py delete -f deployment.yaml
```

## 参数说明

### 全局参数

- `--namespace, -n`: 指定命名空间（默认：default）
- `--all-namespaces, -A`: 所有命名空间
- `--output, -o`: 输出格式（table/json/yaml）
- `--context`: 指定kubectl上下文
- `--kubeconfig`: 指定kubeconfig文件路径

### Pod操作参数

- `--tail`: 显示最后N行日志
- `--follow, -f`: 实时跟踪日志
- `--previous, -p`: 查看之前容器的日志
- `--container, -c`: 指定容器名（多容器Pod）
- `--it`: 交互式TTY

### Deployment参数

- `--image`: 容器镜像
- `--replicas`: 副本数量
- `--port`: 容器端口
- `--env`: 环境变量
- `--dry-run`: 预览变更

### Service参数

- `--type`: Service类型（ClusterIP/NodePort/LoadBalancer）
- `--port`: 服务端口
- `--target-port`: 目标端口
- `--selector`: 标签选择器

## 环境要求

- kubectl >= 1.24
- Kubernetes集群 >= 1.24
- Python >= 3.8
- 有效的kubeconfig配置文件

## 注意事项

1. 确保kubectl已配置并可访问目标集群
2. 生产环境操作前建议使用 `--dry-run` 预览变更
3. 删除操作不可逆，请谨慎使用
4. 大规模扩缩容前请确认集群资源充足
5. 敏感信息建议使用Secret而非ConfigMap

## 示例场景

### 部署Web应用

```bash
# 1. 创建命名空间
kubectl create namespace my-app

# 2. 部署应用
python main.py deployment create web-app \
  --namespace my-app \
  --image nginx:latest \
  --replicas 3 \
  --port 80

# 3. 暴露服务
python main.py service expose deployment web-app \
  --namespace my-app \
  --type LoadBalancer \
  --port 80 \
  --target-port 80

# 4. 查看部署状态
python main.py deployment rollout-status web-app -n my-app

# 5. 查看Pod日志
python main.py pod logs -l app=web-app -n my-app --tail 20
```

### 应用滚动更新

```bash
# 1. 更新镜像版本
python main.py deployment set-image web-app \
  --namespace my-app \
  nginx=nginx:1.21

# 2. 监控滚动状态
python main.py deployment rollout-status web-app -n my-app

# 3. 如有问题，执行回滚
python main.py deployment rollout-undo web-app -n my-app
```

### 排查Pod故障

```bash
# 1. 查看Pod状态和事件
python main.py pod describe problematic-pod

# 2. 查看容器日志
python main.py pod logs problematic-pod --previous

# 3. 进入容器调试
python main.py pod exec problematic-pod -it -- /bin/sh

# 4. 查看资源使用情况
python main.py pod top problematic-pod
```
