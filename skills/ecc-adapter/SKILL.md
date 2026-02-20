---
name: ecc-adapter
description: Everything Claude Code adapter for Kimi Code CLI. Provides sessions, rules, hooks, token optimization, continuous learning, verification, and task orchestration.
---

# Everything Claude Code for Kimi Code CLI

将 Anthropic 黑客松冠军项目 "Everything Claude Code" 适配到 Kimi Code CLI 的完整配置集。

## 已安装组件

### 1. 初始化向导 (`init-wizard.py`)
交互式配置安装工具。

```bash
python ~/.kimi/scripts/init-wizard.py
```

### 2. 规则加载器 (`rules-loader.py`)
多语言规则自动检测与加载。

```bash
# 检测项目语言
python ~/.kimi/scripts/rules-loader.py detect

# 加载规则
python ~/.kimi/scripts/rules-loader.py load

# 安装默认规则
python ~/.kimi/scripts/rules-loader.py install
```

### 3. 会话管理器 (`session_manager.py`)
对标 Claude Code `/sessions` 命令。

```bash
# 列出会话
python ~/.kimi/scripts/session_manager.py list

# 加载会话
python ~/.kimi/scripts/session_manager.py load <id>

# 创建别名
python ~/.kimi/scripts/session_manager.py alias <id> <name>

# 统计信息
python ~/.kimi/scripts/session_manager.py stats
```

### 4. Token 优化器 (`token_optimizer.py`)
模型路由与上下文管理。

```bash
# 查看使用报告
python ~/.kimi/scripts/token_optimizer.py report

# 选择模型
python ~/.kimi/scripts/token_optimizer.py select <task_type>

# 检查是否需要压缩
python ~/.kimi/scripts/token_optimizer.py check --tokens 150000
```

### 5. Hooks 系统 (`hook_runner.py`)
兼容 Claude Code hooks 语义。

```bash
# 生成内置 hooks
python ~/.kimi/scripts/hook_runner.py generate

# 执行 hooks
python ~/.kimi/scripts/hook_runner.py run pre_tool_use --tool Bash --input '{"command":"git push"}'
```

配置位置: `~/.kimi/hooks/hooks.toml`

### 6. 持续学习 (`continuous_learning.py`)
Instinct-based learning system。

```bash
# 记录观测
python ~/.kimi/scripts/continuous_learning.py observe tool_use --data '{"tool":"Read"}'

# 分析模式
python ~/.kimi/scripts/continuous_learning.py analyze

# 查看状态
python ~/.kimi/scripts/continuous_learning.py status

# 进化技能
python ~/.kimi/scripts/continuous_learning.py evolve <instinct_id> --name my-skill
```

### 7. 验证体系 (`verification_system.py`)
Checkpoint, Grader, pass@k。

```bash
# 创建检查点
python ~/.kimi/scripts/verification_system.py checkpoint \
  --description "Feature Complete" \
  --criteria '{"tests_pass":{"type":"exact_match","expected":true}}'

# 运行验证
python ~/.kimi/scripts/verification_system.py eval <checkpoint_id> --state '{"tests_pass":true}'

# 列出检查点
python ~/.kimi/scripts/verification_system.py list
```

### 8. 任务编排器 (`task_orchestrator.py`)
多任务并行执行。

```bash
# 使用模板
python ~/.kimi/scripts/task_orchestrator.py template code-review
python ~/.kimi/scripts/task_orchestrator.py template deploy
python ~/.kimi/scripts/task_orchestrator.py template multi-lang

# 从 JSON 运行
python ~/.kimi/scripts/task_orchestrator.py run tasks.json
```

### 9. 智能缓存 (`smart_cache.py`)
API 和文件缓存。

```bash
# 查看统计
python ~/.kimi/scripts/smart_cache.py stats

# 清空缓存
python ~/.kimi/scripts/smart_cache.py clear
```

## 快速开始

1. **首次安装**:
   ```bash
   python ~/.kimi/scripts/install-all.py
   ```

2. **运行向导**:
   ```bash
   python ~/.kimi/scripts/init-wizard.py
   ```

3. **加载规则**:
   ```bash
   python ~/.kimi/scripts/rules-loader.py load
   ```

## 配置文件

### config.toml
位置: `~/.kimi/config.toml`

```toml
default_model = "kimi-code/kimi-for-coding"
default_thinking = true

[optimization]
max_thinking_tokens = 10000
auto_compact_threshold = 0.5

[rules]
enabled_sets = ["common", "typescript"]

[hooks]
enabled = true
hooks_file = "~/.kimi/hooks/hooks.toml"
```

## 与 Claude Code 的映射

| Claude Code | Kimi Code CLI |
|-------------|---------------|
| `/sessions` | `python ~/.kimi/scripts/session_manager.py` |
| `/plan` | Skill: `plan` |
| `/tdd` | Skill: `tdd` |
| `/checkpoint` | `python ~/.kimi/scripts/verification_system.py checkpoint` |
| `/verify` | `python ~/.kimi/scripts/verification_system.py eval` |
| Hooks | `~/.kimi/hooks/hooks.toml` |
| Rules | `~/.kimi/rules/` |

## 文档

完整报告: `~/everything-claude-code-to-kimi-code-cli-migration-report.md`
