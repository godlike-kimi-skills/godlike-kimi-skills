# Helm Skill

Helm包管理器工具，用于管理Kubernetes应用的Chart生命周期。

## 功能描述

提供完整的Helm Chart管理功能，包括Chart安装、升级、回滚和仓库管理。Use when managing Helm charts, deploying applications with Helm, or when user mentions 'helm', 'chart', 'release', 'helm repo'。

## 能力

- Chart管理：安装、升级、回滚、删除Chart
- Release管理：查看release状态、历史记录、值覆盖
- 仓库管理：添加、更新、删除、搜索Helm仓库
- Chart开发：创建新Chart、打包、验证
- 模板渲染：本地渲染模板、预览输出
- 依赖管理：管理Chart依赖

## 用法

### 仓库管理

```bash
# 列出已添加的仓库
python main.py repo ls

# 添加仓库
python main.py repo add bitnami https://charts.bitnami.com/bitnami

# 更新所有仓库
python main.py repo update

# 搜索Chart
python main.py search repo nginx
python main.py search hub redis

# 删除仓库
python main.py repo remove bitnami
```

### Release管理

```bash
# 列出所有Release
python main.py release ls

# 查看Release状态
python main.py release status my-release

# 查看Release历史
python main.py release history my-release

# 查看Release值
python main.py release values my-release

# 查看Release清单
python main.py release get-manifest my-release
```

### Chart安装

```bash
# 安装Chart（从仓库）
python main.py install my-nginx bitnami/nginx

# 安装Chart（指定版本）
python main.py install my-nginx bitnami/nginx --version 13.2.0

# 安装Chart（从本地目录）
python main.py install my-app ./my-chart

# 安装并设置值
python main.py install my-nginx bitnami/nginx \
  --set service.type=LoadBalancer \
  --set replicaCount=3

# 安装并使用values文件
python main.py install my-nginx bitnami/nginx -f custom-values.yaml

# 生成名称安装
python main.py install bitnami/nginx --generate-name

# 干运行（预览）
python main.py install my-nginx bitnami/nginx --dry-run
```

### Chart升级

```bash
# 升级Release
python main.py upgrade my-nginx bitnami/nginx

# 升级并设置新值
python main.py upgrade my-nginx bitnami/nginx --set replicaCount=5

# 升级并重用上次的值
python main.py upgrade my-nginx bitnami/nginx --reuse-values

# 升级指定版本
python main.py upgrade my-nginx bitnami/nginx --version 13.2.1

# 强制升级（即使没有变化）
python main.py upgrade my-nginx bitnami/nginx --force
```

### 回滚和删除

```bash
# 回滚到指定版本
python main.py rollback my-nginx 2

# 删除Release
python main.py uninstall my-nginx

# 删除并保留历史
python main.py uninstall my-nginx --keep-history

# 批量删除
python main.py uninstall release1 release2 release3
```

### Chart开发

```bash
# 创建新Chart
python main.py create my-chart

# 打包Chart
python main.py package ./my-chart

# 验证Chart
python main.py lint ./my-chart

# 模板渲染（本地测试）
python main.py template my-release ./my-chart -f values.yaml

# 查看Chart信息
python main.py show chart ./my-chart
python main.py show values ./my-chart
python main.py show readme ./my-chart
python main.py show all ./my-chart
```

### 依赖管理

```bash
# 更新依赖
python main.py dependency update ./my-chart

# 构建依赖
python main.py dependency build ./my-chart

# 列出依赖
python main.py dependency list ./my-chart
```

## 参数说明

### 全局参数

- `--kubeconfig`: kubeconfig文件路径
- `--namespace, -n`: 目标命名空间
- `--create-namespace`: 如果不存在则创建命名空间
- `--context`: 使用指定的kubectl上下文
- `--debug`: 启用调试输出

### 安装/升级参数

- `--version`: 指定Chart版本
- `--set`: 设置值（可多次使用）
- `--set-file`: 从文件设置值
- `--set-string`: 将值强制设置为字符串
- `--values, -f`: 指定values文件
- `--dry-run`: 模拟执行，不实际部署
- `--wait`: 等待资源就绪
- `--timeout`: 超时时间

### 回滚参数

- `--cleanup-on-fail`: 失败时清理新资源
- `--force`: 强制重新创建资源
- `--no-hooks`: 跳过hooks执行

### Chart开发参数

- `--sign`: 使用PGP签名
- `--key`: 用于签名的密钥名称
- `--keyring`: 密钥环位置
- `--passphrase-file`: 密码文件
- `--destination, -d`: 打包输出目录

## 环境要求

- Helm >= 3.12
- kubectl >= 1.24
- Kubernetes集群 >= 1.24
- Python >= 3.8

## 注意事项

1. 确保Helm已初始化并可访问集群
2. 生产环境部署前建议使用 `--dry-run` 预览变更
3. 注意Chart版本兼容性
4. 升级前务必备份重要数据
5. 使用版本控制管理values文件

## 示例场景

### 部署Redis集群

```bash
# 1. 添加Bitnami仓库
python main.py repo add bitnami https://charts.bitnami.com/bitnami
python main.py repo update

# 2. 搜索Redis Chart
python main.py search repo redis

# 3. 安装Redis（高可用模式）
python main.py install my-redis bitnami/redis \
  --set architecture=replication \
  --set auth.enabled=true \
  --set auth.password=secret123 \
  --set replica.replicaCount=3

# 4. 查看部署状态
python main.py release status my-redis

# 5. 获取连接信息
python main.py release get-manifest my-redis
```

### CI/CD流水线部署

```bash
# 1. 打包应用Chart
python main.py package ./my-app-chart --destination ./dist

# 2. 验证Chart
python main.py lint ./my-app-chart

# 3. 模板渲染测试
python main.py template my-app ./my-app-chart -f values.prod.yaml

# 4. 部署到生产（带等待和超时）
python main.py upgrade --install my-app ./my-app-chart \
  --namespace production \
  --create-namespace \
  -f values.prod.yaml \
  --wait \
  --timeout 10m

# 5. 验证部署
python main.py release status my-app -n production
```

### Chart开发和测试

```bash
# 1. 创建新Chart
python main.py create my-new-chart
cd my-new-chart

# 2. 编辑Chart.yaml和values.yaml
# ...

# 3. 添加依赖
# 在Chart.yaml中添加依赖

# 4. 更新依赖
python main.py dependency update .

# 5. 本地模板渲染测试
python main.py template test-release . -f values.yaml

# 6. 验证Chart
python main.py lint .

# 7. 本地安装测试
python main.py install test-release . --dry-run

# 8. 打包Chart
python main.py package . --destination ../dist
```

### 回滚操作

```bash
# 1. 查看Release历史
python main.py release history my-app

# 2. 发现有问题的版本
# REVISION    UPDATED                     STATUS      CHART           DESCRIPTION
# 1           Mon Jan  1 10:00:00 2024    superseded  my-app-1.0.0    Install complete
# 2           Mon Jan  1 11:00:00 2024    superseded  my-app-1.1.0    Upgrade complete
# 3           Mon Jan  1 12:00:00 2024    failed      my-app-1.2.0    Upgrade failed

# 3. 回滚到版本2
python main.py rollback my-app 2

# 4. 确认回滚成功
python main.py release history my-app
python main.py release status my-app
```
