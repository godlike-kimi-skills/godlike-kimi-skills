# Pre-Mortem Skill

A structured pre-mortem analysis tool for identifying project risks and preventing failures before they happen. Based on Gary Klein's research showing 30% improvement in risk identification.

## 何时使用本 Skill (Use When)

- Use **before starting any major project** to identify potential failure points
- Use when making **high-stakes decisions** with significant consequences
- Use when the team is **overly optimistic** about a plan's success
- Use for **cross-functional projects** with complex dependencies
- Use when **stakes are high** (large budget, tight deadline, critical outcomes)
- Use when user mentions: `'pre-mortem'`, `'what could go wrong'`, `'why might this fail'`, `'risk analysis'`, `'failure prevention'`, `'before we start'`

## Out of Scope / 不适用范围

- **不替代项目规划**（仅用于风险识别，不制定执行方案）
- **不处理已发生问题**（用于事前预防，不是事后复盘）
- **不适用于低风险日常任务**（用于重要决策，非琐碎事项）
- **不提供具体解决方案**（识别风险后需单独制定应对措施）
- **不保证项目成功**（仅提升风险意识，不消除所有风险）

如需事后分析，请使用 `root-cause-analysis-skill` 或 `five-whys-skill`。

## Core Concept

**Pre-mortem** (from "premortem") is the opposite of post-mortem:
- **Post-mortem**: After death → Analyze what went wrong
- **Pre-mortem**: Before death → Imagine failure and prevent it

### The Psychology Behind It

Research by Gary Klein shows that imagining an event has already failed:
1. **Activates System 2 thinking** (slow, analytical)
2. **Overcomes optimism bias** (natural tendency to underestimate risks)
3. **Triggers prospective hindsight** ("I knew it would fail because...")
4. **Makes it safe to voice concerns** (not pessimism, but preparation)

## Usage Examples

### Example 1: Software Project Launch
```bash
kimi skill pre-mortem-skill analyze \
  --project "Mobile App Launch" \
  --timeline "3 months" \
  --budget "$500K" \
  --team-size 8
```

**Generated Analysis:**
```
╔═══════════════════════════════════════════════════════════╗
║              PRE-MORTEM ANALYSIS REPORT                    ║
║              Project: Mobile App Launch                   ║
╚═══════════════════════════════════════════════════════════╝

🎯 SCENARIO: It's 3 months from now. The app launch failed completely.
             Users abandoned it. The project is considered a disaster.

❌ TOP FAILURE MODES IDENTIFIED:

  1. TECHNICAL DEBT CRISIS (Probability: HIGH)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     • Rushed development led to unstable codebase
     • App crashes on older Android devices
     • API can't handle traffic spikes
     
     Prevention Actions:
     □ Set code quality gates in CI/CD
     □ Test on minimum 10 device types
     □ Load test API to 10x expected traffic

  2. MARKET MISFIT (Probability: MEDIUM-HIGH)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     • Features don't match user expectations
     • Onboarding is too complex
     • Value proposition unclear
     
     Prevention Actions:
     □ Conduct 20 user interviews before launch
     □ Build MVP for beta testing
     □ A/B test onboarding flow

  3. TEAM BURNOUT (Probability: MEDIUM)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     • Unrealistic timeline caused exhaustion
     • Key developer quit mid-project
     • Knowledge silos created bottlenecks
     
     Prevention Actions:
     □ Build in 20% buffer time
     □ Document all critical systems
     □ Cross-train team members
```

### Example 2: Interactive Session
```bash
kimi skill pre-mortem-skill session
```

**Interactive Flow:**
```
🧠 PRE-MORTEM SESSION FACILITATOR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1: Set the Scene
─────────────────────
Project: [User Input]
Timeline: [User Input]
Stake: [User Input]

Step 2: The Mental Time Travel
─────────────────────────────
Imagine it's [future date]. The project has FAILED spectacularly.

What happened? Let's explore failure paths:

Path 1 - Technical Failures:
• What broke technically?
• What integrations failed?
• What wasn't tested enough?

Path 2 - People/Process Failures:
• Who left the team?
• What communication broke down?
• What assumptions were wrong?

Path 3 - External Factors:
• What market changes hurt us?
• What competitors did better?
• What regulations affected us?

Step 3: Prioritize & Act
────────────────────────
High Priority Risks:
1. [Risk] → [Action]
2. [Risk] → [Action]
...
```

### Example 3: Generate Template
```bash
kimi skill pre-mortem-skill template --format markdown --output risk_worksheet.md
```

## Methods & Techniques

### Method 1: Individual Brainstorming
Each team member independently writes failure reasons (5-10 minutes)
- Removes social pressure
- Gets diverse perspectives
- Prevents groupthink

### Method 2: Failure Path Analysis
Trace specific failure chains:
```
Event A → Event B → Final Failure
   ↑
Prevention here stops the chain
```

### Method 3: Category Scanning
Systematically check risk categories:
- **Technical**: Architecture, scalability, security
- **People**: Skills, availability, communication
- **Process**: Timeline, budget, dependencies
- **External**: Market, competition, regulations
- **User**: Adoption, satisfaction, retention

### Method 4: Prospective Hindsight Questions
- "I knew this would fail because..."
- "Looking back, the warning signs were..."
- "We should have seen that coming when..."

## Risk Prioritization Matrix

```
        LOW IMPACT          HIGH IMPACT
       ┌─────────────────┬─────────────────┐
HIGH   │  Monitor        │  CRITICAL       │
PROB   │  (Watch list)   │  (Act now!)     │
       ├─────────────────┼─────────────────┤
LOW    │  Accept         │  Contingency    │
PROB   │  (Ignore)       │  (Plan B)       │
       └─────────────────┴─────────────────┘
```

## Integration with Other Skills

Combine with:
- `five-whys-skill` → Deep dive into root causes
- `bayesian-decision-skill` → Quantify risk probabilities
- `system-thinking-skill` → Map interconnected risks
- `kanban-skill` → Track prevention actions
- `report-in-skill` → Monitor risk status

## Best Practices

### DO:
- ✅ Run pre-mortem **before** finalizing plans
- ✅ Include diverse participants (not just optimists)
- ✅ Make it psychologically safe to voice concerns
- ✅ Focus on **why** things fail, not **if** they fail
- ✅ Document all identified risks
- ✅ Assign owners to prevention actions

### DON'T:
- ❌ Do it after the project starts (too late)
- ❌ Let the most senior person speak first
- ❌ Dismiss concerns as "negativity"
- ❌ Skip the follow-up action planning
- ❌ Treat it as a one-time exercise

## When to Use Pre-Mortem

| Situation | Use Pre-Mortem? | Why |
|-----------|-----------------|-----|
| New product launch | ✅ YES | High uncertainty |
| Major system migration | ✅ YES | Complex dependencies |
| Routine bug fix | ❌ NO | Low stakes |
| Team restructuring | ✅ YES | People risks |
| Updating documentation | ❌ NO | Low impact |
| Strategic partnership | ✅ YES | Irreversible decision |

## Research Backing

- **Gary Klein (2007)**: "Performing a Project Premortem" - Harvard Business Review
- **Deborah Mitchell (1989)**: Prospective hindsight improves prediction accuracy by 30%
- **Daniel Kahneman**: Recommends pre-mortem in "Thinking, Fast and Slow"

## License

MIT License - See LICENSE file
