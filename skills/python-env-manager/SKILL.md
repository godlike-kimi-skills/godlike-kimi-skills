# Python Env Manager

**Python 环境管理工具** - 基于 Pyenv 和 Poetry

Python 版本管理、虚拟环境、依赖锁定。

---

## 核心特性

### 🐍 环境管理

| 功能 | 说明 |
|------|------|
| **版本切换** | 多Python版本管理 |
| **虚拟环境** | 项目隔离环境 |
| **依赖锁定** | requirements/poetry.lock |
| **包管理** | 安装/卸载/更新包 |

### 📦 支持工具

```
pyenv → Python版本管理
poetry → 依赖管理
conda → 科学计算环境
venv → 标准虚拟环境
```

---

## 使用方法

### 安装Python版本
```bash
python-env-manager install 3.12.0
```

### 创建项目环境
```bash
python-env-manager init --python 3.12 --tool poetry
```

### 切换环境
```bash
python-env-manager activate my-project
```

---

## 参考实现

- **Pyenv**: Python 版本管理
- **Poetry**: 依赖管理与打包
- **Conda**: 环境管理系统

---

## 版本信息

- **Version**: 1.0.0
- **Author**: KbotGenesis

---

# 多维度分析报告与改进路线图

## 分析报告

本Skill已通过**第一性原理**、**系统思维**、**贝叶斯决策**、**博弈论**、**精益思想**五个维度进行深度分析。

详细分析报告见: `analysis-reports/python-env-manager-multi-lens-analysis.md`

---

## 核心发现

### 第一性原理分析
- **本质**: 环境管理的本质是**可复现性的保障**
- **基本事实**: 依赖图复杂性、版本冲突、系统差异性、可传递性
- **关键差距**: 缺乏依赖冲突解决、安全漏洞检查、依赖清理
- **改进方向**: 依赖冲突解决、安全集成、智能推荐

### 系统思维分析
- **反馈回路**: 环境膨胀回路(危险) vs 版本碎片化回路(危险)
- **系统层次**: 项目代码→项目依赖→Python解释器→虚拟环境→系统环境
- **改进方向**: 自动清理机制、依赖稳定性调节

### 贝叶斯决策分析
- **版本选择**: 可基于项目特征贝叶斯决策选择Python版本
- **冲突解决**: 方案评估基于P(功能正常)×P(无新冲突)
- **改进方向**: 智能版本推荐、冲突解决方案评估

### 博弈论分析
- **工具选择博弈**: 需要团队协调选择标准工具
- **依赖地狱**: 各包维护者的囚徒困境
- **改进方向**: 统一工具链、语义化版本控制

### 精益思想分析
- **严重浪费**: 等待(安装/下载)、库存(多版本/缓存)、缺陷(环境失败)
- **改进方向**: 本地缓存、并行下载、快速切换

---

## 改进路线图

### 立即实施 (1-2周)

1. **详细使用指南** [P0]
   - 完整的安装和配置步骤
   - 常见用例示例
   - 故障排除指南
   - 各工具对比(pyenv vs conda vs poetry)

2. **依赖冲突解决** [P0]
   - 冲突检测算法
   - 解决方案建议
   - 可视化依赖图
   ```bash
   python-env-manager check --conflicts
   python-env-manager resolve --interactive
   ```

3. **快速开始模板** [P1]
   ```bash
   # 初始化新项目
   python-env-manager init my-project --python 3.11 --tool poetry
   
   # 克隆现有项目
   python-env-manager clone <repo-url> --auto-setup
   
   # 快速切换
   python-env-manager switch --project my-project
   ```

### 短期改进 (1-2个月)

4. **智能推荐** [P1]
   - Python版本推荐（基于项目需求和依赖兼容性）
   - 包选择建议（基于流行度、维护状态）
   - 环境配置模板（Web开发/数据科学/机器学习）
   ```bash
   python-env-manager recommend --project-type web
   # Output: 推荐使用 Python 3.11 + Poetry + FastAPI模板
   ```

5. **安全集成** [P1]
   - 漏洞扫描（集成safety/pyup）
   - 自动修复建议
   - 安全更新通知
   ```bash
   python-env-manager scan --security
   python-env-manager update --security-only
   ```

6. **性能优化** [P2]
   - 并行下载
   - 缓存优化（本地+共享缓存）
   - 快速切换（预激活脚本）
   ```bash
   python-env-manager config --parallel-downloads 4
   python-env-manager config --cache-size 10GB
   ```

7. **依赖分析** [P2]
   - 未使用包检测
   - 依赖树可视化
   - 包大小分析
   ```bash
   python-env-manager analyze --unused
   python-env-manager analyze --tree
   python-env-manager analyze --size
   ```

### 中期愿景 (3-6个月)

8. **环境即代码** [P1]
   - Docker集成
   - CI/CD模板
   - 基础设施即代码
   ```bash
   python-env-manager dockerize --output Dockerfile
   python-env-manager generate-ci --platform github-actions
   ```

9. **智能管理** [P2]
   - 自动清理（未使用版本、过期缓存）
   - 健康监控
   - 预测性维护
   ```bash
   python-env-manager clean --auto
   python-env-manager health
   ```

10. **跨平台保障** [P2]
    - Windows/Linux/macOS统一体验
    - 跨平台锁定文件
    - 可移植环境
    ```bash
    python-env-manager export --platform linux --output env.lock
    python-env-manager import --lock env.lock
    ```

---

## 更新后的架构愿景 (v2.0)

```
Python Env Manager v2.0
├── 版本管理
│   ├── Python安装
│   │   ├── 多版本支持 (3.8-3.12+)
│   │   ├── 快速安装（预编译二进制）
│   │   └── 版本推荐（贝叶斯决策）
│   ├── 版本切换
│   │   ├── 全局切换
│   │   ├── 项目级自动切换
│   │   └── shell集成
│   └── 版本清理
│       ├── 自动检测未使用版本
│       └── 安全删除
├── 虚拟环境
│   ├── 环境创建
│   │   ├── 多种工具支持（venv, conda, poetry, pdm）
│   │   ├── 模板配置
│   │   └── 快速创建
│   ├── 依赖管理
│   │   ├── 依赖解析
│   │   ├── 冲突检测与解决
│   │   ├── 锁定文件
│   │   └── 可视化依赖图
│   └── 环境维护
│       ├── 健康检查
│       ├── 自动清理
│       └── 备份恢复
├── 安全与合规
│   ├── 漏洞扫描
│   │   ├── 已知CVE检查
│   │   └── 许可合规检查
│   ├── 自动修复
│   │   ├── 安全更新建议
│   │   └── 一键修复
│   └── 审计日志
│       ├── 变更记录
│       └── 合规报告
├── 性能优化
│   ├── 缓存管理
│   │   ├── 本地包缓存
│   │   ├── 缓存清理
│   │   └── 缓存共享
│   ├── 并行化
│   │   ├── 并行下载
│   │   └── 并行安装
│   └── 快速切换
│       ├── 预激活环境
│       └── 延迟加载
└── 集成与自动化
    ├── IDE集成
    │   ├── VSCode支持
    │   └── PyCharm支持
    ├── CI/CD模板
    │   ├── GitHub Actions
    │   ├── GitLab CI
    │   └── Jenkins
    └── Docker集成
        ├── Dockerfile生成
        └── 容器化开发环境
```

---

## 使用示例

### 完整项目初始化流程

```bash
# 1. 查看推荐的Python版本
python-env-manager recommend --project-type web
# Output: 推荐使用 Python 3.11（基于性能提升和LTS支持）

# 2. 安装推荐的Python版本
python-env-manager install 3.11.7

# 3. 初始化项目（使用Poetry）
python-env-manager init my-web-app \
  --python 3.11.7 \
  --tool poetry \
  --template fastapi

# 4. 进入项目目录
cd my-web-app

# 5. 添加依赖
python-env-manager add fastapi uvicorn sqlalchemy

# 6. 检查依赖冲突
python-env-manager check --conflicts

# 7. 安全扫描
python-env-manager scan --security

# 8. 生成锁定文件
python-env-manager lock

# 9. 导出Docker配置
python-env-manager dockerize --output Dockerfile

# 10. 生成CI/CD配置
python-env-manager generate-ci --platform github-actions
```

### 依赖冲突解决

```bash
# 检测冲突
$ python-env-manager check --conflicts
⚠️ 发现依赖冲突:
   Package A requires requests>=2.20
   Package B requires requests<2.25

# 查看解决方案
$ python-env-manager resolve --show-options
可选方案:
1. 使用 requests 2.20-2.24 (推荐)
2. 升级 Package B 到 v2.0 (支持requests>=2.20)
3. 降级 Package A 到 v1.5 (支持requests<2.25)

# 自动解决
$ python-env-manager resolve --auto
✅ 已选择方案1: 使用 requests 2.24.0
   所有依赖已满足
```

### 环境健康检查

```bash
$ python-env-manager health

环境健康报告
==============

✅ Python版本: 3.11.7 (最新)
✅ 虚拟环境: 正常
✅ 依赖锁定: 最新
⚠️  安全漏洞: 发现1个中等风险漏洞
   └── urllib3 < 2.0.7 (CVE-2023-45803)
⚠️  未使用包: 发现3个未使用包
   └── pytest-cov, black, isort

建议操作:
1. 运行 `python-env-manager update --security-only` 修复安全漏洞
2. 运行 `python-env-manager clean --unused` 清理未使用包
```

---

## 度量指标

| 指标 | 当前 | 目标 | 测量方法 |
|------|------|------|----------|
| 环境创建时间 | ~5分钟 | <2分钟 | 计时器 |
| 成功率 | ~90% | >99% | 成功/总次数 |
| 依赖解析时间 | ~30s | <10s | 并行优化后 |
| 缓存命中率 | - | >70% | 缓存统计 |
| 安全漏洞发现率 | - | >95% | 扫描结果 |

---

## 与其他Skill的协同

```
Python Env Manager ←→ Coding Agent
    ↓
自动创建适合项目的开发环境

Python Env Manager ←→ Doc Gen Skill
    ↓
管理文档生成工具的依赖

Python Env Manager ←→ One-Click Backup
    ↓
备份重要的虚拟环境配置

Python Env Manager ←→ Git Automation
    ↓
自动配置Git hooks进行依赖检查
```

---

## 最佳实践

### 项目环境策略

```
新项目:
├── 使用Poetry或Pdm（现代依赖管理）
├── Python版本: 3.10+（支持类型提示）
└── 启用锁定文件（确保可复现性）

遗留项目:
├── 评估迁移到现代工具的成本
├── 保留requirements.txt
└── 逐步引入锁定文件

团队项目:
├── 统一工具链（Poetry）
├── 共享缓存服务器
└── CI/CD自动环境验证
```

### 依赖管理最佳实践

```
1. 声明依赖
   ├── 精确指定版本范围
   ├── 区分生产/开发依赖
   └── 记录为什么需要

2. 锁定依赖
   ├── 提交锁定文件到版本控制
   ├── 定期更新锁定文件
   └── 审查更新内容

3. 安全维护
   ├── 定期安全扫描
   ├── 及时更新漏洞包
   └── 监控弃用警告

4. 环境清理
   ├── 移除未使用依赖
   ├── 清理旧Python版本
   └── 定期重建环境验证
```

### CI/CD集成

```yaml
# .github/workflows/python.yml
name: Python CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python Environment
      uses: python-env-manager/action@v1
      with:
        python-version: ${{ matrix.python-version }}
        tool: poetry
    
    - name: Check Dependencies
      run: |
        python-env-manager check --conflicts --strict
        python-env-manager scan --security
    
    - name: Run Tests
      run: |
        python-env-manager run pytest --cov
    
    - name: Check Environment Health
      run: |
        python-env-manager health --strict
```

---

*多维度分析报告生成时间: 2026-02-19*  
*方法论: 第一性原理 + 系统思维 + 贝叶斯决策 + 博弈论 + 精益思想*
