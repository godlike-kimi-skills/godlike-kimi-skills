# Thinking Framework - 元分析

## 概况
| 属性 | 内容 |
|------|------|
| 质量 | ⭐⭐⭐⭐⭐ (5/5) |
| 功能 | 参数化思维工具框架 |
| 特色 | 五层架构 + 可配置模板 |

## 核心创新：参数化思维
```yaml
# 传统思维: 固定模式
"请分析这个问题"

# Thinking Framework: 参数化
analyze:
  depth: detailed|quick
  focus: reasoning|assumptions|concerns  
  scope: local|system|global
  time: short|medium|long
```

## 五层架构的价值
```
UI层 → 用户接口标准化
编排层 → 工具发现与执行  
处理层 → 模板渲染与验证
存储层 → 过程记忆与缓存
集成层 → MCP协议兼容
```
**关键洞察**: 这种分层设计使思维工具可以作为MCP Server被调用！

## 与当前项目的关联
**本项目(10M Token分析)可以受益于**: 
- Think Aloud: 让分析过程可见
- Assumption Check: 验证"36个Lens"的假设
- Fresh Eyes: 定期重新审视进度

## 应用Lens分析

### First Principles视角
- 本质: 思维模板 = 可复用的认知结构
- 突破: 将"思考方式"编码为可调用接口

### System Thinking视角  
- 系统: 工具之间的互操作
- 杠杆点: 模板参数的调整影响全局输出

### Lean Thinking视角
- 浪费: 重复的prompt编写
- 价值流: 从问题→模板→输出
- 流动: 参数化加速响应

## 改进建议
```markdown
## 建议添加的工具

### 1. Multi-Lens Analyzer
```yaml
tool: multi_lens_analyze
parameters:
  topic: "目标主题"
  lenses: [first_principles, system_thinking, toc, bayesian]
  output: synthesis|detailed|comparison
```

### 2. Skill Enhancement Planner
```yaml
tool: skill_enhancement_plan
parameters:
  skill_path: "path/to/skill"
  budget: tokens|time
  priority: p0|p1|p2
  output: roadmap
```
```

## 优先级: P1
- 与本项目目标高度契合
- 可以作为其他Skills的编排框架
- 建议开发增强版模板

---
**Tokens: ~900**
