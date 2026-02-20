# Persistent Agent

**持久化代理系统** - 借鉴 systemd, supervisord, pm2

守护进程管理、自动重启、日志轮转、进程监控。

---

## 核心特性

### 🔄 进程管理

| 功能 | 说明 |
|------|------|
| **自动启动** | 系统启动时自动运行 |
| **崩溃重启** | 失败自动重启，指数退避 |
| **日志管理** | 自动轮转、压缩、清理 |
| **资源限制** | CPU、内存、文件描述符限制 |

### 📊 监控指标

```
监控维度:
├── 进程状态 (运行/停止/崩溃)
├── 资源使用 (CPU/内存/IO)
├── 重启次数
├── 运行时长
└── 日志大小
```

---

## 使用方法

### 管理进程
```bash
# 注册代理
persistent-agent register my-agent --cmd "python app.py" --auto-start

# 启动
persistent-agent start my-agent

# 停止
persistent-agent stop my-agent

# 查看状态
persistent-agent status my-agent

# 查看日志
persistent-agent logs my-agent --follow
```

---

## 参考实现

- **systemd**: Linux系统和服务管理器
- **supervisord**: Python进程管理
- **pm2**: Node.js进程管理器

---

## 配置详解

### 完整配置文件

```yaml
# persistent-agent-config.yaml
agents:
  - name: "trading-bot"
    cmd: "python trading_bot.py --config prod.yaml"
    cwd: "/home/kbot/trading"
    
    # 启动配置
    auto_start: true
    restart_policy: "on-failure"  # always | on-failure | never
    max_restarts: 5
    
    # 指数退避
    backoff:
      initial_delay: 1s
      max_delay: 60s
      multiplier: 2
      
    # 资源限制
    resources:
      cpu_limit: "50%"
      memory_limit: "512MB"
      disk_limit: "1GB"
      
    # 环境变量
    env:
      - "API_KEY=${TRADING_API_KEY}"
      - "LOG_LEVEL=info"
      
    # 健康检查
    health_check:
      enabled: true
      interval: 30s
      timeout: 5s
      retries: 3
      command: "curl -f http://localhost:8080/health"
      
    # 日志配置
    logging:
      stdout: "/var/log/trading-bot.log"
      stderr: "/var/log/trading-bot.error.log"
      max_size: "100MB"
      max_files: 5
      compress: true
      
    # 通知配置
    notifications:
      on_restart: true
      on_failure: true
      channels:
        - slack
        - email
```

### 监控与告警

```bash
# 查看实时状态
persistent-agent status trading-bot --watch

# 查看资源使用
persistent-agent stats trading-bot

# 查看历史重启记录
persistent-agent logs trading-bot --type restart

# 设置告警规则
persistent-agent alert create \
  --agent trading-bot \
  --condition "restart_count > 3 in 1h" \
  --action "notify_admin"
```

---

## 系统架构与反馈机制

### 控制论视角 (生命维持系统)

Persistent Agent是**生命体征维持控制系统**，类比生物自主神经系统：

```
健康参考值 ──→ 生命监测 ──→ 决策引擎 ──→ 执行动作 ──→ 进程状态
     ↑                                            ↓
     └──────────── 生命体征反馈 ←─────────────────┘
```

**控制层次 (生物类比)：**

| 层级 | 生物类比 | 控制对象 | 响应时间 |
|------|----------|----------|----------|
| 自主层 | 脑干反射 | 崩溃重启 | 秒级 |
| 调节层 | 自主神经 | 资源限制 | 分钟级 |
| 意识层 | 大脑皮层 | 策略调整 | 小时级 |

**核心反馈回路：**

| 回路 | 类型 | 描述 |
|------|------|------|
| R1 | 增强 | 可靠性飞轮: 稳定运行→信任积累→更多关键任务→系统重要性 |
| R2 | 增强(负) | 死亡螺旋: 进程崩溃→频繁重启→资源消耗→系统不稳定 |
| B1 | 平衡 | 资源保护环: 资源使用→压力感知→限制触发→资源保护 |
| B2 | 平衡 | 健康校准环: 健康状态→检查频率→问题发现→健康维持 |

### 耗散结构视角 (数字生命)

进程作为开放系统持续与环境交换能量：

```
系统资源 ──→ [启动/维持/恢复] ──→ 服务输出
    ↑                              ↓
    └──── 健康反馈 ←── 监控 ←─────┘
```

**负熵输入**: CPU/内存/IO资源、配置更新、依赖服务  
**熵输出**: 日志记录、监控指标、通知告警

**生命相变临界:**
- C1: 级联故障点 → 熔断隔离
- C2: 性能劣化点 → 资源扩容
- C3: 服务死亡点 → 冷启动恢复

### 非线性生命效应

1. **启动非线性**: 冷启动高消耗，热启动低消耗，预加载近瞬时
2. **故障传播**: 单进程局部影响，关键进程级联影响，依赖环系统瘫痪
3. **恢复非线性**: 简单故障线性恢复，复杂故障指数难度

### 杠杆点

1. **生命观**: 从"进程重启"到"生命维持"
2. **系统目标**: 从"可用性"到"健康度"
3. **信息流**: 全链路健康追踪
4. **反馈延迟**: 实时健康事件
5. **存量规则**: 重启次数上限

### 关键洞察

- **涌现性**: 单进程启停简单，整体服务韧性复杂
- **网络效应**: 依赖图级联脆弱性
- **适应进化**: 故障涨落驱动的策略优化

---

## 故障排查

### 常见问题

| 症状 | 可能原因 | 解决方案 |
|------|----------|----------|
| 启动循环 | 配置错误/依赖缺失 | 检查cmd路径、验证环境 |
| 资源超限 | 内存泄漏 | 优化代码、增加限制 |
| 健康检查失败 | 端口冲突 | 检查端口占用 |
| 日志过大 | 未配置轮转 | 添加logrotate配置 |

### 诊断命令

```bash
# 详细诊断
persistent-agent diagnose trading-bot

# 导出调试信息
persistent-agent debug trading-bot --output debug.zip

# 手动测试启动
persistent-agent test trading-bot --dry-run
```

---

## 版本信息

- **Version**: 2.1.0
- **Author**: KbotGenesis
- **更新**: 添加详细配置和故障排查指南
