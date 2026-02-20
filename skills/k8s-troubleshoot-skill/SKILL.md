# K8s Troubleshoot Skill

Kubernetes故障排查工具，用于诊断Pod问题、网络故障和资源分析。

## 功能描述

提供全面的Kubernetes故障排查能力，包括Pod诊断、网络排查、资源分析和集群健康检查。Use when troubleshooting Kubernetes issues, diagnosing pod failures, or when user mentions 'troubleshoot', 'debug', 'pod crash', 'network problem'。

## 能力

- Pod诊断：容器状态检查、事件分析、崩溃原因排查
- 网络排查：Service连通性、DNS解析、网络策略验证
- 资源分析：CPU/内存使用、资源配额、节点容量
- 存储排查：PV/PVC状态、存储类验证
- 集群健康：节点状态、组件状态、证书检查
- 日志分析：多Pod日志聚合、错误模式识别

## 用法

### Pod故障诊断

```bash
# 诊断Pod（全面检查）
python main.py pod diagnose <pod-name>

# 检查Pod事件
python main.py pod events <pod-name>

# 分析Pod状态
python main.py pod status <pod-name>

# 检查容器退出码
python main.py pod exit-code <pod-name>

# 检查Pod资源限制
python main.py pod resources <pod-name>

# 检查Pod亲和性/反亲和性
python main.py pod affinity <pod-name>
```

### 网络故障排查

```bash
# 检查Service连通性
python main.py network service <service-name>

# DNS解析测试
python main.py network dns <domain>

# 检查网络策略
python main.py network policy -n <namespace>

# 端口连通性测试
python main.py network port <pod-name> <port>

# 检查Ingress配置
python main.py network ingress <ingress-name>

# 网络延迟测试
python main.py network latency <source-pod> <target-pod>
```

### 资源分析

```bash
# 节点资源使用
python main.py resource node

# Pod资源使用
python main.py resource pod -n <namespace>

# 资源配额检查
python main.py resource quota -n <namespace>

# 限制范围检查
python main.py resource limits -n <namespace>

# 检查资源不足问题
python main.py resource pressure

# 容量规划分析
python main.py resource capacity
```

### 存储排查

```bash
# PV状态检查
python main.py storage pv

# PVC状态检查
python main.py storage pvc -n <namespace>

# 存储类检查
python main.py storage class

# 挂载问题诊断
python main.py storage mount <pod-name>
```

### 集群健康检查

```bash
# 全面集群健康检查
python main.py cluster health

# 检查控制平面组件
python main.py cluster control-plane

# 检查节点健康
python main.py cluster nodes

# 证书过期检查
python main.py cluster certs

# 事件聚合分析
python main.py cluster events

# 检查资源泄漏
python main.py cluster leaks
```

### 日志分析

```bash
# 聚合多Pod日志
python main.py logs aggregate -l app=myapp

# 搜索错误日志
python main.py logs errors -l app=myapp --since 1h

# 分析崩溃模式
python main.py logs pattern <pod-name>

# 导出日志到文件
python main.py logs export <pod-name> -o ./logs/
```

## 参数说明

### 全局参数

- `--namespace, -n`: 目标命名空间
- `--all-namespaces, -A`: 所有命名空间
- `--kubeconfig`: kubeconfig文件路径
- `--context`: kubectl上下文
- `--output, -o`: 输出格式（table/json/yaml）
- `--verbose, -v`: 详细输出

### Pod诊断参数

- `--previous, -p`: 查看之前容器的日志
- `--container, -c`: 指定容器
- `--since`: 日志时间范围（如 5m, 1h）

### 网络参数

- `--timeout`: 连接超时时间
- `--retries`: 重试次数
- `--protocol`: 协议（tcp/udp）

### 资源参数

- `--threshold`: 告警阈值（百分比）
- `--sort-by`: 排序字段（cpu/memory）
- `--limit`: 显示数量限制

## 环境要求

- kubectl >= 1.24
- Kubernetes集群 >= 1.24
- Python >= 3.8
- 可选：jq（用于JSON处理）
- 可选：netshoot镜像（用于网络诊断）

## 注意事项

1. 故障排查需要足够的集群权限
2. 网络诊断可能需要netshoot等调试镜像
3. 日志分析可能产生大量输出，建议重定向到文件
4. 生产环境谨慎使用--force等危险操作
5. 建议在测试环境验证修复方案后再应用到生产

## 常见场景排查

### Pod处于Pending状态

```bash
# 1. 查看Pod状态和事件
python main.py pod diagnose my-pod

# 2. 检查资源限制
python main.py resource pressure
python main.py resource quota -n my-namespace

# 3. 检查节点容量
python main.py resource node

# 4. 检查调度约束
python main.py pod affinity my-pod
```

### Pod处于CrashLoopBackOff

```bash
# 1. 查看Pod详情和事件
python main.py pod status my-pod
python main.py pod events my-pod

# 2. 查看容器退出码
python main.py pod exit-code my-pod

# 3. 查看应用日志
python main.py logs errors my-pod --previous

# 4. 分析崩溃模式
python main.py logs pattern my-pod
```

### 网络连接问题

```bash
# 1. 检查Service配置
python main.py network service my-service

# 2. 测试DNS解析
python main.py network dns my-service.default.svc.cluster.local

# 3. 检查网络策略
python main.py network policy -n my-namespace

# 4. 测试Pod间连通性
kubectl run -it --rm debug --image=nicolaka/netshoot --restart=Never -- /bin/bash
```

### 存储挂载失败

```bash
# 1. 检查PVC状态
python main.py storage pvc -n my-namespace

# 2. 检查PV状态
python main.py storage pv

# 3. 检查Pod挂载
python main.py storage mount my-pod

# 4. 检查存储类
python main.py storage class
```

### 节点NotReady

```bash
# 1. 检查节点状态
python main.py cluster nodes

# 2. 查看节点事件
kubectl describe node <node-name>

# 3. 检查资源压力
python main.py resource pressure

# 4. 检查控制平面
python main.py cluster control-plane
```
