# Thinking Framework

**Source**: https://github.com/jcmrs/thinking-tools-framework  
**Stars**: 4.3k+  
**Type**: AI-Augmented Framework  
**Description**: Parameterized prompt templates for systematic analysis

---

## Overview

The Thinking Tools Framework provides **structured thinking prompts** that help AI assistants (and humans) work more effectively by making reasoning processes explicit and repeatable.

**Core Insight**: Thinking tools are **parameterized prompt templates** that guide systematic analysis, planning, and reflection.

---

## The Five Cornerstones

Every tool in the framework embodies these principles:

| Cornerstone | Meaning | Application |
|-------------|---------|-------------|
| **1. Configurability** | Parameterized behavior | Adjust depth, scope, focus |
| **2. Modularity** | Clear separation | Mix and match components |
| **3. Extensibility** | Plugin architecture | Add custom tools |
| **4. Integration** | MCP protocol | Works with existing tools |
| **5. Automation** | Auto-discovery | Hot-reload, validation |

---

## Five-Layer Architecture

```
┌─────────────────────────────────────────────┐
│ Layer 1: UI (CLI, Interfaces)              │
│ → User interaction, command processing      │
├─────────────────────────────────────────────┤
│ Layer 2: Orchestration                     │
│ → Tool discovery, execution flow            │
├─────────────────────────────────────────────┤
│ Layer 3: Processing                        │
│ → Template rendering, validation            │
├─────────────────────────────────────────────┤
│ Layer 4: Storage                           │
│ → Process memory, caching                   │
├─────────────────────────────────────────────┤
│ Layer 5: Integration                       │
│ → MCP server, external tools                │
└─────────────────────────────────────────────┘
```

---

## Built-in Thinking Tools

### Metacognition (3 tools)

#### 1. Think Aloud
Verbalize reasoning process.

```yaml
tool: think_aloud
parameters:
  depth: detailed  # quick/detailed
  focus: reasoning # reasoning/assumptions/concerns

template:
  "I'm thinking about [problem]...
   My current hypothesis is [hypothesis]...
   The key assumptions are [assumptions]...
   What concerns me is [concerns]...
   I'm uncertain about [uncertainties]...
   My next step is [action]"
```

#### 2. Assumption Check
Surface implicit assumptions.

```yaml
tool: assumption_check
parameters:
  thoroughness: high  # low/medium/high
  
template:
  "What am I assuming about:
   - The problem? [List]
   - The solution? [List]
   - The users? [List]
   - The market? [List]
   - The timeline? [List]
   
   Which assumptions are:
   - Untested? [Flag]
   - Critical? [Flag]
   - Questionable? [Flag]"
```

#### 3. Fresh Eyes
Step back and re-evaluate.

```yaml
tool: fresh_eyes
parameters:
  perspective: beginner  # beginner/expert/skeptic
  
template:
  "If I were a [perspective] looking at this:
   - What would confuse me?
   - What questions would I ask?
   - What would I do differently?
   - What am I missing?"
```

### Review (2 tools)

#### 4. Code Review Checklist
Comprehensive quality assessment.

```yaml
tool: code_review
parameters:
  scope: full  # quick/full
  focus: all   # security/performance/maintainability

checklist:
  - [ ] Functionality: Does it work?
  - [ ] Clarity: Is it readable?
  - [ ] Tests: Are there adequate tests?
  - [ ] Security: Any vulnerabilities?
  - [ ] Performance: Any bottlenecks?
  - [ ] Error handling: Edge cases covered?
  - [ ] Documentation: Is it explained?
  - [ ] Maintainability: Can others modify it?
```

#### 5. Architecture Review
System design evaluation.

```yaml
tool: architecture_review
parameters:
  aspect: scalability  # scalability/security/cost

dimensions:
  - Coupling: How interconnected?
  - Cohesion: How focused?
  - Scalability: Growth handling?
  - Flexibility: Change accommodation?
  - Observability: Monitoring coverage?
  - Reliability: Failure handling?
```

### Handoff (2 tools)

#### 6. Session Handover
Zero-information-loss context preservation.

```yaml
tool: session_handover
parameters:
  detail: complete  # summary/complete

sections:
  context:
    - What we were doing
    - Why it matters
    - Current state
    
  decisions:
    - Decisions made
    - Alternatives considered
    - Rationale for choices
    
  next_steps:
    - Immediate next actions
    - Blockers or dependencies
    - Success criteria
    
  knowledge:
    - Key insights
    - Lessons learned
    - Important caveats
```

#### 7. Context Preservation
Quick interruption handling.

```yaml
tool: context_preservation
quick_capture:
  - Current task: [One line]
  - Key thought: [Critical insight]
  - Next action: [What to do next]
  - Blocker: [If any]
```

### Debugging (2 tools)

#### 8. Five Whys
Root cause analysis.

```yaml
tool: five_whys
process:
  problem: [State the problem]
  why1: [Why did it happen?]
  why2: [Why did that happen?]
  why3: [Why did that happen?]
  why4: [Why did that happen?]
  why5: [Root cause identified]
  
solution: [Address root cause, not symptoms]
```

#### 9. Error Analysis
Structured error investigation.

```yaml
tool: error_analysis
sections:
  symptom:
    - What happened?
    - What was expected?
    - What was the impact?
    
  investigation:
    - When did it start?
    - What changed?
    - Where does it occur?
    - Who is affected?
    
  diagnosis:
    - Most likely cause
    - Supporting evidence
    - Alternative hypotheses
    - How to confirm
    
  resolution:
    - Immediate fix
    - Long-term solution
    - Prevention measures
```

---

## Creating Custom Tools

Tool structure:

```yaml
version: "1.0"

metadata:
  name: "my_tool"
  display_name: "My Thinking Tool"
  description: "What this tool helps you do"
  category: "metacognition"
  author: "Your Name"
  tags: ["tag1", "tag2"]

parameters:
  type: "object"
  properties:
    depth:
      type: "string"
      enum: ["quick", "detailed"]
      default: "quick"
  required: []

template:
  source: |
    # Analysis - {{ depth|upper }}
    
    {% if depth == 'quick' %}
    ## Quick Analysis
    - What's the core question?
    - What's the simplest approach?
    {% else %}
    ## Detailed Analysis
    - Context and background
    - Multiple approaches considered
    - Trade-offs and decisions
    {% endif %}
```

---

## Process Memory System

Captures decisions and learnings:

```json
{
  "timestamp": "2026-02-19T23:00:00Z",
  "tool": "architecture_review",
  "context": "Evaluating microservices vs monolith",
  "decision": "Start with modular monolith",
  "rationale": "Team size, speed to market",
  "alternatives_rejected": [
    "Microservices - too complex for team size",
    "Pure monolith - concerned about future scaling"
  ],
  "confidence": "75%",
  "review_date": "2026-03-19"
}
```

---

## Kbot Integration

### Available Commands

```
/think [problem] → Apply think_aloud
/assume → Run assumption_check
/review [code] → Code review
/handoff → Generate session summary
/why [problem] → Five whys analysis
/error [description] → Error analysis
/fresh → Fresh eyes perspective
```

### Workflow Integration

**Before coding**: /assume + /think  
**During coding**: /review (periodic)  
**After error**: /error + /why  
**End session**: /handoff  
**New perspective**: /fresh

---

## 认知架构与思维框架

### 认知透镜分析

本Skill已通过以下认知透镜进行深度分析：

| Lens | 核心洞察 | 关键改进建议 |
|------|----------|--------------|
| **Mental Models** | 第一性原理、逆向思维、OODA循环 | 增加执行后审查、完成OODA闭环 |
| **Reasoning Tools** | 情报分析、形式验证、设计思维 | 增加竞争性假设、创造性工具 |
| **Critical Thinking** | 分析瘫痪、锚定效应 | 足够好判断标准、多初始假设 |
| **Socratic Inquiry** | 模板化局限、文化差异 | 明确适用范围、自适应模板 |
| **First-Order Logic** | 参数选择、质量定义 | 必要参数强制、多维度权重 |

### 认知结构评估

| 维度 | 评分 | 核心发现 |
|------|------|----------|
| 概念清晰度 | 9/10 | Five Cornerstones定义明确 |
| 工具完备性 | 7/10 | 覆盖主要思考类型，有缺口 |
| 可操作性 | 8/10 | 参数化设计实用 |
| 可扩展性 | 8/10 | 自定义工具机制清晰 |
| 元认知深度 | 7/10 | 缺少对思考本身的反思 |

### 核心认知模型

**思考工具的认知基础**:
```
问题输入 → 工具选择 → 参数配置 → 结构化处理 → 洞察输出
                ↓
         认知负荷管理
                ↓
         效率-深度权衡
```

**认知增强方向**:
1. **创造性工具**: Brainstorming、SCAMPER、lateral thinking
2. **概率工具**: 贝叶斯更新、蒙特卡洛模拟
3. **伦理工具**: 利益相关者分析、伦理框架
4. **情感工具**: 情感检查、直觉验证
5. **跨文化工具**: 多元视角整合

### 推荐工具链

| 场景 | 推荐工具链 |
|------|------------|
| 新问题探索 | Think Aloud → Assumption Check → Fresh Eyes |
| 方案评估 | Architecture Review + 领域特定分析 |
| 故障排查 | Error Analysis → Five Whys |
| 会话结束 | Session Handover |
| 定期复盘 | Process Memory Review |

### 相关认知资源

- [完整认知分析报告](./COGNITIVE_ANALYSIS.md)
- 关联Skill: `mental-models-v2`, `reasoning-tools`, `critical-thinking`, `socratic-inquiry`, `first-order-logic`

---

*Systematic thinking, repeatable results.*
