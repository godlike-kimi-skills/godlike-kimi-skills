# K8s Troubleshoot Skill 使用示例

## 示例1：Pod故障排查

### Pod处于Pending状态

```bash
# 全面诊断Pod
python main.py pod diagnose my-pod

# 输出示例：
# 🔍 Pod诊断报告: my-pod
# ================================
# 状态: Pending
# 命名空间: default
# 节点: <none>
# 
# ⚠️ 发现问题:
# 1. Pod未被调度
# 2. 可能原因: 资源不足 / 节点选择器不匹配 / 亲和性约束
#
# 💡 建议操作:
# 1. 检查节点资源: python main.py resource node
# 2. 检查节点选择器: kubectl get pod my-pod -o yaml | grep nodeSelector
```

### Pod处于CrashLoopBackOff

```bash
# 分析Pod状态
python main.py pod status my-crashing-pod

# 检查容器退出码
python main.py pod exit-code my-crashing-pod

# 分析崩溃模式
python main.py logs pattern my-crashing-pod

# 查看详细事件
python main.py pod events my-crashing-pod --since 1h

# 输出示例：
# 📊 Pod状态分析: my-crashing-pod
# ================================
# 状态: CrashLoopBackOff
# 重启次数: 15
# 最后状态: Terminated
# 退出码: 1
# 原因: Error
# 
# 🔍 日志分析:
# - 发现错误: "Connection refused to database"
# - 建议: 检查数据库服务是否运行，验证连接字符串
```

## 示例2：网络故障排查

### Service无法访问

```bash
# 检查Service配置和连通性
python main.py network service my-service

# DNS解析测试
python main.py network dns my-service.default.svc.cluster.local

# 检查网络策略
python main.py network policy -n default

# 输出示例：
# 🌐 Service诊断: my-service
# ================================
# 类型: ClusterIP
# ClusterIP: 10.96.0.1
# 端口: 80/TCP → 8080
# Endpoints: 3
# 
# ✅ 健康检查:
# - Service配置正确
# - 所有Endpoints健康
# - DNS解析正常
```

### Ingress问题排查

```bash
# 检查Ingress配置
python main.py network ingress my-ingress

# 测试外部访问
python main.py network ingress my-ingress --test-external

# 输出示例：
# 🌐 Ingress诊断: my-ingress
# ================================
# Host: app.example.com
# 后端Service: my-service:80
# 
# ⚠️ 问题发现:
# - Ingress控制器未配置默认证书
# - 建议: 配置TLS证书或添加默认后端
```

## 示例3：资源问题排查

### 节点资源不足

```bash
# 检查所有节点资源
python main.py resource node

# 检查资源压力
python main.py resource pressure

# 容量规划
python main.py resource capacity

# 输出示例：
# 📊 节点资源分析
# ================================
# Node: worker-1
# CPU: 85% / 89% (请求/限制) ⚠️
# 内存: 72% / 78% (请求/限制)
# 
# 🔴 高负载节点: worker-1
# 建议: 考虑添加新节点或优化Pod资源请求
```

### Pod资源超限

```bash
# 检查Pod资源使用
python main.py resource pod -n production

# 检查特定Pod资源
python main.py pod resources my-pod

# 检查资源配额
python main.py resource quota -n production

# 输出示例：
# 📊 Pod资源分析: my-pod
# ================================
# CPU请求: 100m / 500m (20%)
# 内存请求: 256Mi / 512Mi (50%)
# 
# ⚠️ CPU使用率接近限制
# 建议: 增加CPU限制或优化应用性能
```

## 示例4：存储问题排查

### PVC无法绑定

```bash
# 检查PVC状态
python main.py storage pvc -n default

# 检查PV
python main.py storage pv

# 检查存储类
python main.py storage class

# 输出示例：
# 💾 PVC诊断
# ================================
# PVC: my-pvc
# 状态: Pending
# 容量请求: 10Gi
# 存储类: standard
# 
# ⚠️ 问题: 无可用PV
# 建议: 
# 1. 检查StorageClass配置
# 2. 手动创建匹配的PV
# 3. 启用动态供给
```

### 挂载失败诊断

```bash
# 诊断Pod存储挂载
python main.py storage mount my-pod

# 输出示例：
# 💾 存储挂载诊断: my-pod
# ================================
# 卷: data-volume
# 类型: PVC
# 挂载路径: /data
# 
# ❌ 挂载错误
# 错误: "unable to mount, fs type not supported"
# 建议: 安装必要的文件系统工具或更换存储类
```

## 示例5：集群健康检查

### 全面健康检查

```bash
# 执行全面集群健康检查
python main.py cluster health

# 输出示例：
# 🏥 集群健康检查报告
# ================================
# 总体状态: ⚠️ 警告
# 
# 控制平面: ✅ 健康
# - API Server: 运行中
# - etcd: 健康
# - Controller Manager: 运行中
# - Scheduler: 运行中
# 
# 节点状态: ⚠️ 警告
# - 就绪节点: 2/3
# - NotReady: worker-3 (Kubelet未响应)
# 
# 证书状态: ✅ 健康
# - 所有证书有效期 > 30天
```

### 证书过期检查

```bash
# 检查证书过期时间
python main.py cluster certs

# 输出示例：
# 🔐 证书检查
# ================================
# API Server证书:  expires in 180 days ✅
# etcd证书:        expires in 200 days ✅
# 前端代理证书:    expires in 15 days ⚠️
# 
# ⚠️ 即将过期证书:
# - 前端代理证书将在15天内过期
# 建议: 执行 kubeadm certs renew 更新证书
```

## 示例6：日志分析

### 错误日志聚合

```bash
# 聚合应用错误日志
python main.py logs errors -l app=myapp -n production --since 2h

# 输出示例：
# 📝 错误日志聚合 (过去2小时)
# ================================
# 总错误数: 156
# 
# 错误分布:
# - Connection refused: 89 (57%)
# - Timeout: 45 (29%)
# - 5xx errors: 22 (14%)
# 
# 受影响Pod:
# - myapp-7d9f4b8c5-x2abc: 67 errors
# - myapp-7d9f4b8c5-y3def: 54 errors
# 
# 🔍 分析:
# 主要问题为连接拒绝，建议检查下游服务状态
```

### 导出日志用于分析

```bash
# 导出Pod日志
python main.py logs export my-pod -o ./logs/

# 导出多Pod日志
python main.py logs export -l app=myapp -n production -o ./logs/

# 输出示例：
# 📁 日志导出完成
# ================================
# 导出目录: ./logs/
# 导出Pod数: 5
# 总日志大小: 15.2 MB
# 时间范围: 2024-01-01 00:00 - 2024-01-01 12:00
```

## 示例7：实际故障场景

### 场景1：应用无法启动

```bash
# 步骤1: 诊断Pod
python main.py pod diagnose my-app

# 步骤2: 查看资源
python main.py resource pod -n default

# 步骤3: 检查事件
python main.py pod events my-app --since 30m

# 步骤4: 分析日志
python main.py logs errors my-app

# 常见原因和解决方案:
# 1. 镜像拉取失败 -> 检查镜像名称和仓库访问
# 2. 资源不足 -> 调整资源请求或添加节点
# 3. 配置错误 -> 检查ConfigMap/Secret挂载
# 4. 健康检查失败 -> 调整探针配置
```

### 场景2：服务间歇性不可用

```bash
# 步骤1: 检查Pod状态
python main.py pod status -l app=myapp

# 步骤2: 网络诊断
python main.py network service my-service
python main.py network latency my-pod-1 my-pod-2

# 步骤3: 资源压力
python main.py resource pressure

# 步骤4: 日志分析
python main.py logs pattern -l app=myapp

# 常见原因:
# 1. OOMKilled -> 增加内存限制
# 2. CPU限制 -> 增加CPU配额
# 3. 网络策略 -> 检查并调整网络策略
# 4. 节点压力 -> 分散Pod或添加节点
```

### 场景3：存储性能问题

```bash
# 步骤1: 检查存储状态
python main.py storage pv
python main.py storage pvc -n production

# 步骤2: 检查Pod挂载
python main.py storage mount my-db-pod

# 步骤3: I/O性能测试
kubectl exec my-db-pod -- iostat -x 1 5

# 常见优化:
# 1. 使用SSD存储类
# 2. 调整PV大小
# 3. 优化应用I/O模式
# 4. 使用本地存储（如适用）
```
