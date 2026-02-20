# Kubernetes Skill 使用示例

## 示例1：快速部署Nginx应用

```bash
# 创建Deployment
python main.py deployment create nginx-app \
  --image nginx:latest \
  --replicas 2 \
  --port 80

# 查看Deployment状态
python main.py deployment ls

# 暴露为Service
python main.py service expose deployment nginx-app \
  --type NodePort \
  --port 80 \
  --target-port 80

# 查看Service
python main.py service ls

# 查看Pod状态
python main.py pod ls

# 查看Pod日志
python main.py pod logs -l app=nginx-app
```

## 示例2：滚动更新应用

```bash
# 初始部署
python main.py deployment create my-web \
  --image myapp:v1.0 \
  --replicas 3

# 更新到新版本
python main.py deployment set-image my-web myapp=myapp:v2.0

# 监控滚动更新进度
python main.py deployment rollout-status my-web

# 查看更新历史
python main.py deployment rollout-history my-web

# 如有问题，回滚到上一版本
python main.py deployment rollout-undo my-web

# 回滚到特定版本
python main.py deployment rollout-undo my-web --to-revision 2
```

## 示例3：自动扩缩容

```bash
# 部署应用
python main.py deployment create api-server \
  --image myapi:1.0 \
  --replicas 2

# 手动扩容到5个副本
python main.py deployment scale api-server --replicas 5

# 设置自动扩缩容（需要metrics-server）
kubectl autoscale deployment api-server --min=2 --max=10 --cpu-percent=70

# 查看HPA状态
kubectl get hpa api-server
```

## 示例4：使用ConfigMap和Secret

```bash
# 创建ConfigMap
python main.py configmap create app-config \
  --from-literal=DB_HOST=postgres \
  --from-literal=DB_PORT=5432 \
  --from-literal=LOG_LEVEL=info

# 从文件创建ConfigMap
python main.py configmap create nginx-config \
  --from-file=nginx.conf

# 创建Secret
python main.py secret create db-credentials \
  --from-literal=username=admin \
  --from-literal=password=secret123

# 部署应用并使用配置
python main.py deployment create backend \
  --image mybackend:1.0 \
  --env-from-configmap app-config \
  --env-from-secret db-credentials
```

## 示例5：故障排查

```bash
# 1. 查看集群整体状态
python main.py cluster info

# 2. 查看节点资源使用
python main.py node ls
python main.py node top

# 3. 查看问题Pod
python main.py pod ls --all-namespaces | grep -i error

# 4. 查看Pod详细事件
python main.py pod describe problematic-pod

# 5. 查看容器日志（包括之前崩溃的容器）
python main.py pod logs problematic-pod
python main.py pod logs problematic-pod --previous

# 6. 进入容器调试
python main.py pod exec problematic-pod -it -- /bin/sh

# 7. 端口转发进行本地调试
python main.py pod port-forward problematic-pod 8080:80

# 8. 查看资源使用情况
kubectl top pod problematic-pod
kubectl describe node <node-name>
```

## 示例6：多环境管理

假设有开发、测试、生产三个环境：

```bash
# 创建不同命名空间
kubectl create namespace dev
kubectl create namespace staging
kubectl create namespace production

# 在开发环境部署
python main.py apply -f k8s/ --namespace dev

# 在测试环境部署
python main.py apply -f k8s/ --namespace staging

# 查看各环境Pod
python main.py pod ls -n dev
python main.py pod ls -n staging
python main.py pod ls -n production

# 跨命名空间操作
python main.py pod ls --all-namespaces
```

## 示例7：YAML模板部署

deployment-template.yaml：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ app_name }}
  labels:
    app: {{ app_name }}
spec:
  replicas: {{ replicas }}
  selector:
    matchLabels:
      app: {{ app_name }}
  template:
    metadata:
      labels:
        app: {{ app_name }}
    spec:
      containers:
      - name: app
        image: {{ image }}
        ports:
        - containerPort: {{ port }}
        resources:
          requests:
            memory: "{{ memory_request }}"
            cpu: "{{ cpu_request }}"
          limits:
            memory: "{{ memory_limit }}"
            cpu: "{{ cpu_limit }}"
```

部署命令：

```bash
# 应用模板
python main.py apply -f deployment-template.yaml \
  --set app_name=myapp \
  --set replicas=3 \
  --set image=myapp:v1.0 \
  --set port=8080
```

## 示例8：定时任务（CronJob）管理

```bash
# 创建CronJob
kubectl create cronjob backup-job \
  --image=backup-tool:latest \
  --schedule="0 2 * * *" \
  -- /bin/backup-script.sh

# 查看CronJobs
kubectl get cronjobs

# 查看Job执行历史
kubectl get jobs

# 手动触发一次Job
kubectl create job --from=cronjob/backup-job manual-backup-001

# 删除CronJob及其Job
kubectl delete cronjob backup-job
```
