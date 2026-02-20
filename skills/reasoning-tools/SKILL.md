# Reasoning Tools

**Source**: https://github.com/dvdarkin/reasoning-tools  
**Stars**: 12.8k+  
**Type**: Knowledge Base  
**Description**: 500+ transferable reasoning primitives from 34 high-value domains

---

## Overview

A comprehensive library of **reasoning primitives** — mental operations that transfer across domains. Not facts, not theories, but thinking tools that remain useful even when specific models are wrong.

Each tool includes:
- **What**: The core concept
- **Why it matters**: What problem it solves  
- **The key move**: The actual mental operation
- **Classic application**: Where it originated
- **Surprising application**: Evidence it transfers
- **Failure modes**: When it misleads

---

## The 34 Domains

### Decision Under Uncertainty (4)
1. **Bayesian Statistics** - Rigorous framework for updating beliefs with evidence
2. **Meteorology** - Ensemble forecasting, confidence intervals, model averaging
3. **Intelligence Analysis** - Structured analytic techniques, red teaming, hypothesis testing
4. **Emergency Medicine** - Triage protocols, rapid assessment under pressure

### Persuasion & Influence (3)
5. **Game Theory (Signaling)** - Costly signals, credible commitments, information revelation
6. **Social Psychology** - Cognitive biases, attitude change, group dynamics
7. **Classical Rhetoric** - Persuasive argumentation, audience analysis, rhetorical appeals

### Creative Generation (2)
8. **Design Thinking** - Human-centered problem solving, prototyping, iteration
9. **Evolutionary Biology** - Variation, selection, adaptation, convergent evolution

### Complex System Analysis (4)
10. **System Dynamics** - Stock-flow thinking, feedback loops, delays
11. **Network Science** - Graph structure, centrality, clustering, cascades
12. **Ecology** - Niche construction, trophic levels, succession, resilience
13. **Accident Investigation** - Root cause analysis, Swiss cheese model

### Skill Acquisition & Mastery (3)
14. **Learning Theory** - Spaced repetition, retrieval practice, transfer
15. **Sports Science** - Deliberate practice, periodization, skill acquisition
16. **Expertise Studies** - Pattern recognition, chunking, mental models

### Coordination & Cooperation (3)
17. **Mechanism Design** - Incentive compatibility, revelation principle
18. **Organizational Behavior** - Team dynamics, culture, motivation, structure
19. **Constitutional Design** - Separation of powers, checks and balances

### Truth-Seeking & Verification (4)
20. **Formal Verification** - Proofs, invariants, model checking
21. **Experimental Design** - Controls, randomization, blinding, replication
22. **Investigative Journalism** - Source verification, documentary evidence
23. **Logic & Critical Thinking** - Valid inference, fallacy detection

### Conflict & Competition (3)
24. **Military Strategy** - Force concentration, interior lines, maneuver warfare
25. **Competitive Game Theory** - Nash equilibrium, minimax, backward induction
26. **Litigation Strategy** - Discovery, burden of proof, adversarial system

### Resource Allocation (6)
27. **Economics - Core** - Opportunity cost, marginal analysis, comparative advantage
28. **Information Economics** - Adverse selection, moral hazard, signaling
29. **Behavioral Economics** - Loss aversion, framing, anchoring
29. **Operations Research** - Optimization, queuing theory, linear programming
31. **Portfolio Management** - Diversification, risk-adjusted returns, rebalancing
32. **Distributive Justice** - Fairness principles, allocation criteria

### Pattern Recognition (2)
33. **Machine Learning** - Bias-variance tradeoff, regularization, cross-validation
34. **Medical Diagnostics** - Differential diagnosis, base rates, likelihood ratios

---

## Quick Application

### For Decision Problems
```
Domain: Decision Under Uncertainty
Tool: Bayesian Update
Move: Start with base rate, adjust with evidence strength
Kbot Use: Kill criteria thresholds, pivot decisions
```

### For System Problems
```
Domain: Complex System Analysis
Tool: Feedback Loop Analysis
Move: Identify R (reinforcing) vs B (balancing) loops
Kbot Use: Growth loops, cost constraints in business model
```

### For People Problems
```
Domain: Coordination & Cooperation
Tool: Mechanism Design
Move: Align incentives so truth-telling is optimal
Kbot Use: Partner alignment, automated reporting
```

---

## Cross-Domain Tools

| Tool | Application |
|------|-------------|
| **Base Rate Integration** | Start with prior probability before new evidence |
| **Ensemble Forecasting** | Multiple models weighted by past accuracy |
| **Red Teaming** | Structured challenge of own position |
| **Root Cause Analysis** | 5 Whys + Swiss cheese model |
| **Costly Signaling** | Credible commitments through sacrifice |
| **Margin of Safety** | Buffer for unknown unknowns |

---

## 深度认知分析: 推理工具的偏差防御机制

### 1. 认知偏差维度分析 (Cognitive Biases Lens)

推理工具库是**认知偏差的跨领域疫苗库**。34个高价值领域的500+推理原语，每个都是从特定错误中提炼的免疫血清。

**领域特异性偏差的通用解**: 医学诊断中的**基础概率忽略**与商业预测中的**基础概率忽略**本质相同。工具库从Medical Diagnostics提取的"Base Rate Integration"可移植到任何概率判断场景，实现一次学习、处处适用。

**对抗过度自信的多元校验**: 单一领域的自信可能源于**邓宁-克鲁格效应**。工具库要求同时调用Ensemble Forecasting（气象学）、Red Teaming（情报分析）、Cross-validation（机器学习）三种技术，从多角度挑战判断，构建**认知免疫系统**。

**确认偏差的结构性中和**: Experimental Design领域的"Blinding"（盲法）直接对抗观察者偏差；Intelligence Analysis的"Structured Analytic Techniques"要求显式列出反对假设；Investigative Journalism的"Source Verification"强制寻找独立证据。三重机制形成纵深防御。

**可得性偏差的概率化修正**: 多个领域工具直接针对可得性启发——Bayesian Statistics要求显式先验、Medical Diagnostics强调基础率、Portfolio Management要求历史回测。这些工具共同构建**统计直觉**，替代**记忆直觉**。

### 2. 行为经济学维度分析 (Behavioral Economics Lens)

工具库是行为经济学的**领域扩展包**，将心理学洞察转化为可操作的跨领域工具。

**损失厌恶的领域映射**: Behavioral Economics直接作为第29个领域存在，但损失厌恶的影响渗透到多个领域工具中——Emergency Medicine的Triage（优先处理最可能存活者）对抗"试图拯救所有人"的损失厌恶；Military Strategy的"Economy of Force"要求接受必要损失；Portfolio Management的"止损规则"预设退出点。

**框架效应的跨领域免疫**: Classical Rhetoric领域的"Audience Analysis"和"Framing"工具，将框架从潜意识影响提升为有意识的工具。理解修辞框架后，可以识别商业提案、新闻报道、政治言论中的框架操控，实现**框架免疫**。

**现时偏差的时间工具**: Learning Theory的"Spaced Repetition"和Sports Science的"Periodization"都是对抗**双曲折现**的技术——通过预设计划约束当下冲动，将长期目标分解为即时反馈循环。

**社会偏差的机制设计**: Mechanism Design领域的"Incentive Compatibility"和"Revelation Principle"直接针对**信息不对称**和**策略性隐瞒**。Constitutional Design的"Checks and Balances"是对**权力集中偏差**的制度化防御。

### 3. 助推理论维度分析 (Nudge Theory Lens)

推理工具库提供了**自我选择架构**的设计原则，帮助构建引导理性决策的环境。

**默认选项的认知设计**: 工具库中的"Base Rate Integration"建议将统计基准设为默认起点；"Margin of Safety"要求将风险缓冲设为默认配置。这些设计原则可用于构建个人决策系统，让理性成为默认、冲动成为例外。

**反馈回路的结构嵌入**: System Dynamics的"Stock-Flow Thinking"和"Feedback Loops"直接指导设计学习系统；Expertise Studies的"Deliberate Practice"强调即时反馈的重要性。这些工具帮助构建**纠错反馈回路**，使偏差在发生后立即被识别和修正。

**简化复杂选择的启发式**: 面对复杂决策时，Operations Research的"Optimization"可能过于计算密集。工具库提供简化版本——Game Theory的"Dominant Strategy"检查（是否存在无论他人如何选择都是最优的选项）；Decision Analysis的"Minimax Regret"（最小化最大后悔）。

**承诺机制的增强设计**: Costly Signaling（昂贵信号）工具解释了为何"付出沉没成本"能增强承诺可信度。可以利用这一原理设计自我承诺装置——公开宣布目标（Social Psychology）、设置不可撤销的截止日期（Mechanism Design）、投入不可回收的资源（Game Theory）。

### 4. 决策疲劳维度分析 (Decision Fatigue Lens)

500+工具的庞大集合似乎增加认知负荷，但设计良好的工具调用系统实际上是**认知卸载机制**。

**程序化决策的构建**: Emergency Medicine的"Triage Protocols"展示了如何将复杂决策转化为流程图。工具库支持为常见决策场景构建类似的**决策树**——当条件A满足时执行工具X，否则执行工具Y，将困难判断转化为模式匹配。

**启发式分层系统**: 工具库按领域组织，支持**分层调用**——面对问题时，先确定领域（这是决策问题？系统问题？人际问题？），再选择具体工具。这种分层结构避免在海量工具中搜索，将选项空间从500+压缩到10-20个相关工具。

**认知外包协议**: 多个工具支持将部分决策外包给外部结构——Ensemble Forecasting依赖群体智慧；Red Teaming引入外部挑战者；Formal Verification使用自动化证明。这些工具帮助识别可以**自动化或委托**的决策环节。

**能量管理的领域轮换**: 不同领域工具消耗不同认知资源——Mathematical Optimization需要高度集中，而Design Thinking的"Prototyping"允许直觉探索。工具库支持根据当前认知状态选择匹配的工具类型，避免在疲劳时强行使用高耗能工具。

### 5. 选择架构维度分析 (Choice Architecture Lens)

推理工具库是**认知选择架构的构建套件**，提供设计更好决策环境的组件。

**选项生成的扩展**: Evolutionary Biology的"Variation"工具和Design Thinking的"Ideation"技术直接对抗**选项窄化**——当直觉只提供1-2个选项时，这些工具强制生成更多可能性。Creative Generation类别本身就是选项扩展器。

**属性评估的多维展开**: 工具库要求从34个领域审视问题，这种**多维度展开**是对**聚焦错觉**的强力解药。例如评估一个商业机会，不仅要考虑经济回报（Economics），还要考虑系统效应（System Dynamics）、竞争反应（Game Theory）、执行难度（Skill Acquisition）、伦理影响（Distributive Justice）。

**信息排序的时序设计**: Accident Investigation的"5 Whys"要求从表面现象深入到根本原因；Root Cause Analysis的"Swiss Cheese Model"要求检视多层防御的失效。这些工具规定了**信息处理的深度顺序**，避免过早聚焦于症状而非病因。

**错误容忍的架构设计**: Machine Learning的"Bias-Variance Tradeoff"直接承认所有模型都有错误，关键是平衡两种错误类型；"Regularization"技术防止过度拟合（即过度反应于噪声）。这些工具支持构建**容错决策系统**，承认不完美并设计纠错机制。

---

## 领域-偏差映射表

| 目标偏差 | 推荐领域 | 关键工具 |
|----------|----------|----------|
| 确认偏差 | Intelligence Analysis | Red Teaming, ACH |
| 可得性启发 | Medical Diagnostics | Base Rate Integration |
| 过度自信 | Machine Learning | Cross-validation, Ensemble |
| 锚定效应 | Behavioral Economics | Multiple anchors generation |
| 沉没成本 | Economics | Marginal Analysis |
| 损失厌恶 | Portfolio Management | Stop-loss rules |
| 群体思维 | Organizational Behavior | Devil's advocate structure |
| 规划谬误 | Operations Research | PERT, Critical Path |
| 后见之明 | Experimental Design | Pre-registration |
| 控制错觉 | System Dynamics | Feedback loop mapping |

---

## Kbot Integration

Use these tools for:
- **Pre-launch**: Red team your business model
- **Validation**: Base rate + evidence updating
- **Scaling**: System dynamics + network effects
- **Crisis**: Emergency medicine triage protocols

### 决策前检查清单

```
调用推理工具前确认:
□ 已识别问题类型（决策/系统/人际/冲突/资源）
□ 已检查对应领域的认知偏差清单
□ 已应用至少2个不同领域的工具交叉验证
□ 已考虑工具的Failure Modes
□ 已设计反馈机制验证决策结果
```

---

*523 tools. 34 domains. Infinite applications.*
*Domain expertise is knowing which tool to use when.*
*Meta-expertise is knowing your tools' blind spots.*
