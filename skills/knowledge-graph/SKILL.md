# Knowledge Graph

**Source**: https://github.com/noduslabs/infranodus-obsidian-plugin  
**Stars**: 2.9k+  
**Type**: Knowledge Visualization Tool  
**Description**: Knowledge graph + AI text analysis for Obsidian

---

## Overview

InfraNodus creates **knowledge graphs** from text — visualizing ideas as nodes and their connections as edges. It reveals patterns, gaps, and bridges in your thinking.

---

## Core Concepts

### Knowledge Graph Structure

```
    ┌───────┐         ┌───────┐
    │ Idea A │───────>│ Idea B │
    └───┬───┘         └───┬───┘
        │                 │
        ↓                 ↓
    ┌───────┐         ┌───────┐
    │ Idea C │<───────│ Idea D │
    └───────┘         └───────┘
```

- **Nodes**: Concepts, entities, ideas
- **Edges**: Relationships, co-occurrences
- **Clusters**: Related idea groups
- **Gaps**: Missing connections

### Text to Graph Pipeline

```
Raw Text → Tokenization → Entity Extraction → 
Relationship Detection → Graph Construction → Visualization
```

---

## Graph Analysis Techniques

### 1. Centrality Analysis
Which ideas are most connected?

| Metric | Meaning | Use Case |
|--------|---------|----------|
| **Degree** | Number of connections | Most referenced ideas |
| **Betweenness** | Bridge between clusters | Key connectors |
| **Closeness** | Shortest path to all others | Core concepts |
| **Eigenvector** | Connected to important nodes | Influential ideas |

### 2. Community Detection
Finding natural groupings.

```
Cluster 1 (Blue):     Cluster 2 (Red):
├─ Revenue            ├─ Users
├─ Pricing            ├─ Acquisition
└─ Monetization       └─ Retention

Bridge: "Conversion" connects both clusters
```

### 3. Gap Analysis
What's missing from the graph?

```
Dense connection:    Sparse connection:
Marketing ── Sales   Product ─────── ?
   │            │      │
   └─── Fast ───┘      └─── Slow ───?

Gap identified: Product feedback loop weak
```

### 4. Topic Modeling
Extracting themes from graph structure.

```
Topic 1 (40%): Revenue & Business Model
Topic 2 (30%): User Experience
Topic 3 (20%): Technical Architecture
Topic 4 (10%): Marketing Strategy
```

---

## Graph Types

### 1. Co-occurrence Graph
Words appearing together.

```
"Build AI-driven revenue system"

Build ── AI ── Revenue ── System
         │       │
      Driven    (root)
```

### 2. Concept Hierarchy
Ideas organized by abstraction.

```
                Business Strategy
                      │
      ┌───────────────┼───────────────┐
      ↓               ↓               ↓
   Marketing      Operations      Finance
      │               │               │
   ┌──┴──┐        ┌───┴───┐      ┌───┴───┐
   ↓     ↓        ↓       ↓      ↓       ↓
  SEO  Content   Automation  Metrics  Revenue  Costs
```

### 3. Causal Graph
Cause-effect relationships.

```
Investment ──(+)>── Capability ──(+)>── Quality
                                             │
                                             ↓(+)
Revenue <────(+)───── Users <──────── Satisfaction
```

### 4. Semantic Graph
Meaning-based connections.

```
Startup ──[similar to]──> Small Business
    │
    └──[type of]──> Company
    │
    └──[has]──> Risk
```

---

## Kbot Applications

### 1. Document Analysis
```
Input: Business plan document

Graph Output:
├─ Top concepts: Revenue, Users, AI, Automation
├─ Clusters: Technical, Business, Marketing
├─ Gaps: Competitive analysis weak
└─ Bridges: "Monetization" connects tech and business
```

### 2. Knowledge Synthesis
```
Input: 50 research papers on crypto trading

Graph Output:
├─ Central themes: Risk management, Algorithms, Markets
├─ Emerging ideas: AI prediction, On-chain analysis
├─ Gaps: Regulatory considerations underrepresented
└─ Insights: Technical analysis declining in importance
```

### 3. Decision Mapping
```
Input: Pros/cons of pivot decision

Graph Output:
├─ Pro cluster: Market opportunity, Better fit
├─ Con cluster: Sunk cost, Execution risk
├─ Bridge nodes: Time to market, Team capabilities
└─ Recommendation: Pivot (strong pro cluster density)
```

### 4. Conversation Analysis
```
Input: Meeting transcript

Graph Output:
├─ Topics discussed: Feature roadmap, Bugs, Timeline
├─ Topic balance: 60% bugs, 30% roadmap, 10% timeline
├─ Concerns: Quality repeatedly mentioned
└─ Action items: Test coverage needs discussion
```

---

## Graph Query Language

### Basic Queries

```
FIND nodes WHERE concept = "revenue"
→ Returns: Revenue node and connections

FIND paths FROM "idea" TO "action"
→ Returns: All reasoning chains

FIND clusters WITH density > 0.5
→ Returns: Well-formed topic groups

FIND gaps BETWEEN "cluster_a" AND "cluster_b"
→ Returns: Missing connections
```

### Advanced Queries

```
ANALYZE centrality OF "business_model"
→ Returns: Degree, betweenness, importance

COMPARE graphs "plan_v1" AND "plan_v2"
→ Returns: Added, removed, modified concepts

TRACK evolution OF "strategy" OVER time
→ Returns: How concept developed

SUGGEST bridges FOR disconnected_clusters
→ Returns: Potential connecting concepts
```

---

## Visual Patterns

### Healthy Knowledge Graph
- Multiple well-connected clusters
- Clear bridges between clusters
- Balanced node distribution
- Few orphaned nodes

### Warning Signs
- Giant central node (over-reliance on one concept)
- Disconnected islands (silos)
- Sparse periphery (underexplored areas)
- Dense core with no bridges (echo chamber)

---

## Integration Commands

```
/graph "[text]" → Create graph from text
/analyze "[text]" → Full graph analysis
/compare [doc1] [doc2] → Compare knowledge graphs
/gap "[text]" → Identify knowledge gaps
/synthesize [folder] → Merge multiple documents
```

---

## 认知架构与思维框架

### 认知透镜分析

本Skill已通过以下认知透镜进行深度分析：

| Lens | 核心洞察 | 关键改进建议 |
|------|----------|--------------|
| **Mental Models** | 网络效应、地图与领土、涌现性 | 增加关系权重、时间维度、层次结构 |
| **Reasoning Tools** | 网络科学应用、系统动力学缺失 | 增加因果循环图、反馈回路识别 |
| **Critical Thinking** | 确认偏误风险、幸存者偏差 | 增加异常模式高亮、反方视角功能 |
| **Socratic Inquiry** | 共现≠语义关联、静态图的局限 | 引入多视角验证、动态演化支持 |
| **First-Order Logic** | 相关性启发式的逻辑问题 | 引入置信度量化、假设形式化 |

### 认知结构评估

| 维度 | 评分 | 核心发现 |
|------|------|----------|
| 概念清晰度 | 7/10 | 核心概念定义良好，边界需明确 |
| 推理严密性 | 6/10 | 启发式为主，形式化空间较大 |
| 假设透明度 | 5/10 | 关键假设未完全声明 |
| 反脆弱性 | 6/10 | 有错误处理但不够系统 |
| 可验证性 | 6/10 | 部分指标可量化 |

### 核心认知模型

**知识表示的认知基础**:
```
节点(概念) --关系--> 节点(概念)
    ↓              ↓
 激活强度      关系类型/权重
    ↓              ↓
 中心性计算    推理链构建
```

**认知增强方向**:
1. **动态知识演化**: 支持知识的时间维度变化
2. **不确定性处理**: 节点/边带置信度权重
3. **多视角支持**: 不同抽象层次的交互式探索
4. **跨Skill集成**: 与Reasoning Tools、Memory的联动

### 相关认知资源

- [完整认知分析报告](./COGNITIVE_ANALYSIS.md)
- 关联Skill: `mental-models-v2`, `reasoning-tools`, `critical-thinking`, `first-order-logic`

---

## 网络效应深度分析

### Network Effects 网络效应分析

知识图谱是典型的**直接网络效应**系统，其价值遵循梅特卡夫定律的变体——网络价值与连接数量的平方成正比。在知识图谱中，每个新增概念节点不仅增加一个信息点，更通过与现有节点的潜在连接产生组合价值。当节点数量达到临界规模（约50-100个核心概念）时，图谱开始涌现"知识洞察"能力：自动发现隐性关联、识别结构洞、预测知识缺口。

**连接密度效应**: 知识图谱的连接密度遵循幂律分布，少数核心概念（度中心性高）成为知识枢纽，连接多个知识社群。这种结构使得信息检索路径大大缩短——从任意概念到达目标概念的平均路径长度随网络规模呈对数增长而非线性增长。当知识图谱跨越不同领域（技术、商业、市场），跨领域连接产生的"弱关系"价值成为创新突破的主要来源。

**价值增长曲线**: 知识图谱呈现S型价值增长曲线——初期积累缓慢（冷启动问题），达到临界质量后进入指数增长期，最终因认知负荷饱和进入平台期。关键策略是通过自动化文本导入降低内容生产成本，加速跨越冷启动阶段。

### Platform Strategy 平台战略分析

知识图谱具有**双边平台**特征，连接"知识生产者"（内容创作者、数据输入者）与"知识消费者"（查询者、分析者）。平台的核心价值主张是降低知识发现成本——将分散的信息转化为结构化的可导航网络。

**平台治理机制**: 知识图谱需要建立内容质量标准（节点定义规范、关系类型约束）和激励机制（贡献度可视化、知识影响力排名）。平台的关键控制点是图算法（中心性计算、社区发现）——算法决定了哪些知识被凸显、哪些关联被推荐，实质上是平台的"编排权"。

**网络外部性内化**: 知识图谱通过API开放将网络外部性转化为平台收入——每个新用户的使用都会改进图谱质量（反馈循环），而平台通过数据服务收费捕获这部分价值。平台战略的终极目标是成为"知识基础设施"——当其他Skills和系统依赖知识图谱作为知识组织标准时，平台获得持久竞争优势。

### Ecosystem Design 生态设计分析

知识图谱在Skill生态中扮演**知识枢纽**角色，与多个Skills形成紧密耦合：

**上游依赖**: 从`long-term-memory`获取历史知识沉淀，从`firecrawl`等数据获取Skill接收结构化/非结构化数据输入。

**下游赋能**: 为`workflow-builder`提供决策知识支撑，为`alert-manager`提供根因分析知识库，为`bayesian-decision`提供先验知识结构。

**横向协同**: 与`mental-models-v2`共享认知框架本体，与`reasoning-tools`共享推理路径表示。

**生态位战略**: 知识图谱的生态位是"知识互操作层"——通过标准化知识表示（RDF/属性图）使不同Skills的知识能够互通。生态设计的核心挑战是平衡标准化（互操作性）与灵活性（领域适配），解决方案是提供可扩展的本体框架和自定义关系类型机制。

### Viral Growth 病毒式增长分析

知识图谱的增长机制是**内容驱动型病毒传播**——高质量图谱本身就是最有力的营销工具。当用户发现图谱揭示了其未曾意识到的知识关联时，产生"认知惊喜"，驱动分享行为。

**增长飞轮**: 用户导入内容 → 图谱自动生成洞察 → 用户分享洞察 → 新用户被吸引 → 更多内容导入。

**病毒系数优化**: 降低首次使用价值门槛（提供模板图谱）、增加社交分享触点（一键生成分享图）、设计协作功能（多人共建图谱）提升病毒系数K值。

**增长瓶颈**: 知识图谱面临"内容冷启动"和"认知过载"双重瓶颈。解决方案包括：AI辅助内容导入（降低生产成本）、智能图谱摘要（降低消费成本）、渐进式披露（根据用户熟悉度动态调整图谱复杂度）。

### Two-Sided Markets 双边市场分析

知识图谱连接的两边是**知识供给方**（拥有领域知识的内容创作者）和**知识需求方**（寻求问题解决方案的决策者）。

**交叉网络效应**: 供给方越多 → 图谱覆盖领域越广 → 需求方价值越高 → 需求方增长 → 供给方影响力扩大 → 更多供给方加入。这种正反馈循环一旦启动，形成自我强化的增长引擎。

**定价策略**: 对需求方采用免费增值模式（基础图谱功能免费，高级分析付费）；对供给方采用影响力代币机制（知识贡献转化为平台声誉和收益分成）。

**市场均衡挑战**: 双边市场面临"鸡蛋问题"——没有供给方吸引不来需求方，没有需求方激励不了供给方。解决策略是"种子内容"策略：平台初期投入资源构建高质量基础图谱，证明价值后吸引双边用户。

---

*Visualize thinking. Find connections. Discover gaps.*
