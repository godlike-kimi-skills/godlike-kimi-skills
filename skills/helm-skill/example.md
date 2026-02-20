# Helm Skill 使用示例

## 示例1：部署Nginx应用

```bash
# 1. 添加Bitnami仓库
python main.py repo add bitnami https://charts.bitnami.com/bitnami

# 2. 更新仓库索引
python main.py repo update

# 3. 搜索Nginx Chart
python main.py search repo nginx

# 4. 安装Nginx
python main.py install my-nginx bitnami/nginx

# 5. 查看Release状态
python main.py release status my-nginx

# 6. 查看部署的服务
kubectl get svc my-nginx
```

## 示例2：自定义配置部署

```bash
# 使用values文件部署
python main.py install my-app stable/my-app \
  --namespace production \
  --create-namespace \
  -f values-production.yaml \
  --set replicaCount=3 \
  --set service.type=LoadBalancer \
  --wait \
  --timeout 10m

# 部署时传递敏感数据（不记录）
python main.py install my-db bitnami/postgresql \
  --set auth.password=secret123 \
  --set auth.postgresPassword=adminpass
```

## 示例3：升级和回滚

```bash
# 查看当前Release
python main.py release ls

# 升级到新版本
python main.py upgrade my-nginx bitnami/nginx --version 14.0.0

# 升级并修改配置
python main.py upgrade my-nginx bitnami/nginx \
  --set replicaCount=5 \
  --set resources.limits.memory=512Mi

# 查看升级历史
python main.py release history my-nginx

# 回滚到指定版本
python main.py rollback my-nginx 1

# 删除Release
python main.py uninstall my-nginx
```

## 示例4：Chart开发完整流程

```bash
# 1. 创建新Chart
python main.py create my-custom-app
cd my-custom-app

# 2. 编辑Chart.yaml
cat > Chart.yaml <<EOF
apiVersion: v2
name: my-custom-app
description: My custom application Chart
type: application
version: 0.1.0
appVersion: "1.0.0"
dependencies:
  - name: postgresql
    version: 12.x.x
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled
EOF

# 3. 编辑values.yaml
# ... 自定义配置 ...

# 4. 更新依赖
python main.py dependency update .

# 5. 本地模板渲染测试
python main.py template test-release . -f values.yaml > rendered.yaml

# 6. 验证Chart
python main.py lint .

# 7. 本地安装测试（dry-run）
python main.py install test-release . --dry-run

# 8. 打包Chart
python main.py package . --destination ../charts

# 9. 发布到仓库（可选）
# helm repo index ../charts --url https://mycharts.example.com
```

## 示例5：多环境管理

```bash
# 创建命名空间
kubectl create namespace dev
kubectl create namespace staging
kubectl create namespace production

# values-dev.yaml
replicaCount: 1
service:
  type: ClusterIP
resources:
  limits:
    cpu: 100m
    memory: 128Mi

# values-production.yaml
replicaCount: 3
service:
  type: LoadBalancer
resources:
  limits:
    cpu: 500m
    memory: 512Mi
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10

# 部署到不同环境
python main.py install my-app ./my-chart -n dev -f values-dev.yaml
python main.py install my-app ./my-chart -n staging -f values-staging.yaml
python main.py install my-app ./my-chart -n production -f values-production.yaml

# 查看各环境状态
python main.py release ls -n dev
python main.py release ls -n staging
python main.py release ls -n production
```

## 示例6：复杂应用部署（依赖管理）

```bash
# Chart.yaml
apiVersion: v2
name: ecommerce-app
description: E-commerce application with dependencies
type: application
version: 1.0.0
appVersion: "2.0.0"
dependencies:
  - name: postgresql
    version: 12.x.x
    repository: https://charts.bitnami.com/bitnami
    alias: db
  - name: redis
    version: 17.x.x
    repository: https://charts.bitnami.com/bitnami
    alias: cache
  - name: rabbitmq
    version: 11.x.x
    repository: https://charts.bitnami.com/bitnami
    condition: messaging.enabled

# 更新依赖
python main.py dependency update .

# 安装应用（包含所有依赖）
python main.py install ecommerce ./ecommerce-app \
  --set db.auth.password=dbpass \
  --set cache.auth.password=cachepass \
  --set messaging.enabled=true
```

## 示例7：CI/CD集成

```yaml
# .github/workflows/deploy.yml
name: Deploy with Helm

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Helm
        uses: azure/setup-helm@v3
      
      - name: Lint Chart
        run: |
          python main.py lint ./charts/my-app
      
      - name: Template Test
        run: |
          python main.py template test-release ./charts/my-app -f values.ci.yaml
      
      - name: Package Chart
        run: |
          python main.py package ./charts/my-app --destination ./dist
      
      - name: Deploy to Staging
        run: |
          python main.py upgrade --install my-app ./charts/my-app \
            --namespace staging \
            --create-namespace \
            -f values.staging.yaml \
            --wait \
            --timeout 5m
```

## 示例8：备份和恢复

```bash
# 导出Release值
python main.py release values my-app > my-app-values-backup.yaml

# 导出Release清单
python main.py release get-manifest my-app > my-app-manifest-backup.yaml

# 查看Release历史（用于恢复）
python main.py release history my-app

# 灾难恢复：重新安装并恢复配置
python main.py install my-app-restored ./my-chart -f my-app-values-backup.yaml
```

## 示例9：仓库管理

```bash
# 添加多个常用仓库
python main.py repo add stable https://charts.helm.sh/stable
python main.py repo add bitnami https://charts.bitnami.com/bitnami
python main.py repo add jetstack https://charts.jetstack.io
python main.py repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
python main.py repo add prometheus-community https://prometheus-community.github.io/helm-charts
python main.py repo add grafana https://grafana.github.io/helm-charts

# 更新所有仓库
python main.py repo update

# 查看仓库列表
python main.py repo ls

# 搜索Chart（本地仓库）
python main.py search repo postgresql

# 搜索Chart（Helm Hub）
python main.py search hub redis
```

## 示例10：调试和故障排查

```bash
# 查看Release事件
python main.py release status my-app

# 查看Release详细清单
python main.py release get-manifest my-app

# 查看Release历史
python main.py release history my-app

# 渲染模板（本地调试）
python main.py template debug-release ./my-chart \
  --debug \
  -f values.yaml \
  > debug-output.yaml

# 测试安装（dry-run）
python main.py install test-release ./my-chart --dry-run --debug

# 查看被渲染的notes
python main.py release get-notes my-app
```
