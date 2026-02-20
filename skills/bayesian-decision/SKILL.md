# Bayesian Decision

**Source**: reasoning-tools domain extract  
**Type**: Decision Framework  
**Description**: Rigorous framework for updating beliefs with evidence

---

## Bayes' Theorem

```
P(H|E) = P(E|H) × P(H) / P(E)

Posterior = Likelihood × Prior / Evidence
```

## Key Components

| Component | Meaning | Example |
|-----------|---------|---------|
| **Prior P(H)** | Initial belief | 15% success rate for similar projects |
| **Likelihood P(E\|H)** | Evidence if true | 80% of successful projects have MVP |
| **Evidence P(E)** | Total probability of evidence | Weighted average |
| **Posterior P(H\|E)** | Updated belief | New success probability |

## Belief Update Protocol

```
DECISION: [What we're evaluating]

PRIOR (Base Rate):
- Industry average success: X%
- Our track record: Y%
- Starting confidence: Z%

EVIDENCE:
- [+] Positive indicator: +10%
- [-] Negative indicator: -15%
- [?] Uncertain: ±5%

POSTERIOR (Updated Confidence):
- Calculated: XX%
- Decision threshold: >70% proceed, <30% kill, 30-70% gather more data

NEXT ACTION: [Based on threshold]
```

## Decision Thresholds

| Posterior | Action | Meaning |
|-----------|--------|---------|
| >70% | **Proceed** | Strong evidence for success |
| 30-70% | **Gather More** | Inconclusive, need data |
| <30% | **Kill** | Weak prospects, cut losses |

## Kill Criteria Application

```
Kill Trigger Probability:
- Start: 20% (base failure rate)
- After 10min no engagement: 35%
- After 1hr no revenue signal: 50%
- After 6hr no transaction: 70% → CONSIDER KILL
- After 24hr negative ROI: 85% → KILL
```

---

## 多证据序贯更新

当获得多个证据时，可以序贯更新：

```
Step 1: P(H) → P(H|E1)
Step 2: P(H|E1) → P(H|E1,E2)  [将Step 1的后验作为Step 2的先验]
Step 3: P(H|E1,E2) → P(H|E1,E2,E3)
```

### 实际案例: 产品发布决策

**背景**: 考虑是否提前发布新产品

**先验**: 提前发布成功率 P(Success) = 30%

**证据1**: 竞品延迟发布
- P(竞品延迟|成功) = 70%  [成功产品往往让竞品紧张]
- P(竞品延迟|失败) = 30%  [失败产品竞品不关注]
- P(竞品延迟) = 0.7×0.3 + 0.3×0.7 = 42%

**更新**: 
P(Success|竞品延迟) = 0.7×0.3 / 0.42 = 50%

**证据2**: 早期用户反馈积极
- P(积极反馈|成功) = 80%
- P(积极反馈|失败) = 20%
- P(积极反馈) = 0.8×0.5 + 0.2×0.5 = 50%

**更新**:
P(Success|积极反馈) = 0.8×0.5 / 0.5 = 80%

**决策**: 80%成功率 > 70%阈值， Proceed!

---

## 认知偏差修正

### 基础概率忽略 (Base Rate Neglect)
**问题**: 过度关注具体证据，忽略基础概率

**修正**: 始终从合理的基础概率开始
```
❌ "这个团队很强，成功率90%!"
✅ "行业基础成功率20%，团队强+30%，调整后50%"
```

### 确认偏差 (Confirmation Bias)
**问题**: 只关注支持既有观点的证据

**修正**: 主动寻找反面证据
```
EVIDENCE:
[+] 支持证据: 权重 × 0.7
[-] 反面证据: 权重 × 1.3  [故意加权]
[?] 不确定: 保持开放
```

### 过度自信 (Overconfidence)
**问题**: 概率估计过于极端

**修正**: 向50%回归
```
原始估计: 90%
校准后: 90% × 0.8 + 50% × 0.2 = 82%
```

---

## 深度认知分析: 偏差识别与纠偏机制

### 1. 认知偏差维度分析 (Cognitive Biases Lens)

贝叶斯决策框架本质上是一套**偏差纠偏系统**。人类决策中存在数十种系统性偏差，而贝叶斯定理提供了数学化的修正路径。

**代表性偏差纠偏**: 当人们看到"优秀团队"时，直觉判断成功率90%，这是典型代表性启发。贝叶斯要求先问"行业基础成功率多少？"，强制引入基础概率锚定，将估计从90%拉回更理性的50%。

**可得性偏差对抗**: 近期成功案例容易被回忆，导致高估成功概率。贝叶斯要求显式定义先验P(H)，强制决策者基于统计数据而非记忆碎片构建概率。

**确认偏差的结构性修正**: 贝叶斯公式的分母P(E)必须包含正反两面的证据计算。这种数学结构强制要求考虑"如果假设不成立，观察到该证据的概率"，从算法层面打破确认偏差循环。

**过度自信的回归机制**: 贝叶斯更新是一个收敛过程，无论先验多么极端，随着证据积累，后验都会向真实值收敛。这种数学特性为决策者提供了"谦逊机制"。

### 2. 行为经济学维度分析 (Behavioral Economics Lens)

从卡尼曼的前景理论视角看，贝叶斯决策框架修正了人类决策中的**非理性概率加权**。

**概率加权函数的校准**: 人类对小概率事件过度加权（买彩票），对中高概率事件加权不足（买保险）。贝叶斯计算使用客观概率P(E|H)，而非主观加权π(P)，强制使用线性概率而非S型加权曲线。

**损失厌恶的数学中和**: 前景理论中损失效用是收益的2.25倍。贝叶斯框架通过**决策阈值**机制（<30%放弃，>70%进行）将这种情绪反应转化为客观标准，避免在损失域的风险寻求行为。

**框架效应的免疫**: 同一问题以不同方式呈现（存活率90% vs 死亡率10%）会导致不同选择。贝叶斯要求量化所有数值，将语言框架转化为数学公式，使表达方式不再影响结论。

**现时偏差的延迟机制**: 贝叶斯更新是序贯过程，要求"等待更多证据"区间（30-70%），这种设计强制对抗"现在就决定"的冲动，为理性分析争取时间。

### 3. 助推理论维度分析 (Nudge Theory Lens)

贝叶斯框架是**选择架构**的经典应用，通过设计决策环境引导理性选择。

**默认选项设计**: 框架要求"从基础概率开始"，将统计基准设为默认起点，而非直觉判断。这种默认设置强制决策者经历"为何偏离基准"的反思过程。

**反馈机制嵌入**: 每次证据更新后，后验概率的显式计算提供了即时反馈。这种反馈回路强化了"证据驱动信念"的行为模式，弱化"信念驱动证据搜索"的确认偏差。

**简化复杂选择**: 将无限可能的后验概率简化为三个行动区间（Proceed/Gather/Kill），这种**分类助推**降低了决策负荷，同时保留关键区分度。

**社会证明的替代**: 贝叶斯要求明确定义"我们的追踪记录"作为先验成分，将社会比较转化为个人历史数据的客观参考，减少对他人行为的盲目跟随。

### 4. 决策疲劳维度分析 (Decision Fatigue Lens)

贝叶斯框架通过**程序化决策**减少认知资源消耗。

**预承诺机制**: 在决策前就设定阈值（70%/30%），将困难的价值判断从"当下"转移到"事前"。当面对具体决策时，只需简单比较数值与阈值，无需重新评估"何时放弃"。

**自动化更新流程**: 序贯更新公式提供了机械化的计算路径。一旦建立框架，后续证据处理变成填表式的程序化工作，减少每次重新分析的认知负荷。

**决策分流策略**: 框架将决策分为"证据收集"和"行动选择"两个阶段。在信息不足时（30-70%区间），明确推迟行动决策，专注于数据收集，避免在疲劳状态下做重大判断。

**Kill Criteria的止损自动化**: 将止损规则转化为概率阈值，当系统触发时自动执行，避免损失厌恶导致的"再等等看"拖延行为。这种**预设退出机制**是应对决策疲劳的关键设计。

### 5. 选择架构维度分析 (Choice Architecture Lens)

贝叶斯框架是**精心设计的决策环境**，通过结构引导优化选择。

**信息排序设计**: 要求按"先验→证据→后验"顺序组织信息，这种结构强制决策者先建立基准，再考虑新信息，避免**首因效应**导致的过度锚定。

**选项数量控制**: 将连续的后验概率空间压缩为三个行动选项（Proceed/Gather/Kill），这种**选项简化**符合选择超载理论，在保留决策精度的同时降低认知复杂度。

**属性显著性提升**: 通过显式表格展示P(H)、P(E|H)、P(E)等参数，将原本隐含的假设置于显著位置。这种**信息透明化**设计让潜在的认知偏差暴露于可审视的状态。

**错误容错设计**: 框架允许多轮序贯更新，每次更新都可以修正之前的估计。这种**迭代结构**承认人类判断的不完美，提供了持续改进的通道，而非追求一次性完美决策。

---

## 快速参考卡

```
/bayesian
  Decision: [待评估的决策]
  Prior: [基础概率]%
  Evidence:
    - [证据1]: [对成功的影响]
    - [证据2]: [对成功的影响]
  Threshold: [决策阈值]%
```

---

## 纠偏检查清单

使用贝叶斯框架时，确认已规避以下偏差：

- [ ] **基础概率忽略**: 是否从合理基准开始？
- [ ] **确认偏差**: 是否主动寻找反面证据？
- [ ] **过度自信**: 概率估计是否经过校准？
- [ ] **可得性偏差**: 是否基于统计数据而非记忆？
- [ ] **锚定效应**: 初始值是否合理，更新是否充分？
- [ ] **损失厌恶**: 是否使用阈值而非情绪做决策？
- [ ] **现时偏差**: 是否在不确定区间选择收集更多数据？

---

*Update beliefs, not just information.*
*Use math to defeat cognitive biases.*
