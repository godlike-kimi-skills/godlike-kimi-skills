# Pre-Mortem Skill 🔮

A structured pre-mortem analysis tool for identifying project risks and preventing failures before they happen.

> **"By imagining failure, we make success more likely."** - Gary Klein

## Overview

**Pre-mortem** is a decision-making technique where you imagine a project has already failed, then work backward to identify potential causes. Research shows this improves risk identification by **30%**.

This skill helps you:
- 🔍 Identify hidden risks before starting projects
- 🛡️ Prevent costly failures through early preparation
- 🧠 Overcome natural optimism bias
- 📊 Prioritize risks by severity
- ✅ Create actionable prevention plans

## Installation

```bash
# Clone the repository
git clone https://github.com/your-org/godlike-kimi-skills.git

# Install the skill
kimi skills install ./skills/pre-mortem-skill
```

## Quick Start

### 1. Quick Analysis
```bash
kimi skill pre-mortem-skill analyze \
  --project "Mobile App Launch" \
  --description "New e-commerce mobile application" \
  --timeline "3 months" \
  --stakeholders "Dev Team,Product Manager,Marketing"
```

### 2. Interactive Session
```bash
kimi skill pre-mortem-skill session
```

### 3. Generate Worksheet Template
```bash
kimi skill pre-mortem-skill template --format markdown --output risk_worksheet.md
```

## Usage Examples

### Example 1: Software Project

```bash
kimi skill pre-mortem-skill analyze \
  --project "API Migration" \
  --description "Migrating legacy APIs to microservices" \
  --timeline "6 months"
```

**Sample Output:**
```
╔═══════════════════════════════════════════════════════════╗
║                   🔮 PRE-MORTEM ANALYSIS                  ║
║              Project: API Migration                       ║
╚═══════════════════════════════════════════════════════════╝

🎭 FAILURE SCENARIO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Imagine it's 6 months from now...
The project 'API Migration' has FAILED spectacularly.

❌ TOP FAILURE MODES IDENTIFIED:

  1. TECHNICAL DEBT CRISIS (Probability: HIGH)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     • Service boundaries incorrectly defined
     • Data consistency issues across services
     • Performance degradation under load
     
     Prevention Actions:
     □ Conduct thorough domain modeling
     □ Implement distributed transaction patterns
     □ Load test to 10x expected traffic
     ...
```

### Example 2: Interactive Session

```bash
$ kimi skill pre-mortem-skill session

🧠 INTERACTIVE PRE-MORTEM SESSION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1: Project Information
─────────────────────
Project name: E-commerce Platform
Brief description: New B2B marketplace
Timeline (e.g., '3 months'): 4 months
Key stakeholders: Engineering, Product, Sales

🤖 Generating initial risk library...
✅ Identified 10 potential risks.

Step 2: Add Custom Risks
─────────────────────
What specific failure modes worry you?

Risk description: Payment integration fails
Category: 1. technical
Probability: 2. high
Prevention action: Test with sandbox first
✓ Risk added!

[Report generated...]
```

## Risk Categories

The skill analyzes risks across six categories:

| Category | Examples |
|----------|----------|
| **🔧 Technical** | Architecture, scalability, security, integrations |
| **👥 People** | Team skills, availability, communication, burnout |
| **📋 Process** | Timeline, budget, scope, dependencies |
| **🌍 External** | Market, competition, regulations, economy |
| **👤 User** | Adoption, satisfaction, onboarding, retention |
| **💰 Financial** | Revenue, costs, funding, pricing |

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

## When to Use Pre-Mortem

### ✅ Use Pre-Mortem When:
- Starting a **new major project**
- Making **high-stakes decisions**
- **Budget > $100K** or **timeline > 3 months**
- **Cross-functional** dependencies exist
- **Low tolerance for failure** (healthcare, finance, etc.)
- Team is **overly optimistic**

### ❌ Skip Pre-Mortem When:
- Routine maintenance tasks
- Low-risk, reversible decisions
- Tight deadline (use post-mortem instead)

## Best Practices

### DO:
- ✅ Run pre-mortem **before** finalizing plans
- ✅ Include diverse participants
- ✅ Focus on **why** things fail
- ✅ Document all risks
- ✅ Assign owners to prevention actions
- ✅ Schedule follow-up reviews

### DON'T:
- ❌ Do it after project starts
- ❌ Let senior person speak first
- ❌ Dismiss concerns as "negativity"
- ❌ Skip action planning
- ❌ Treat as one-time exercise

## Integration with Other Skills

Combine with:
- `five-whys-skill` → Deep dive into root causes
- `bayesian-decision-skill` → Quantify risk probabilities  
- `system-thinking-skill` → Map interconnected risks
- `kanban-skill` → Track prevention actions
- `report-in-skill` → Monitor risk status

## The Science Behind It

### Research Foundation

**Gary Klein (2007)** - "Performing a Project Premortem"
- Harvard Business Review
- Showed 30% improvement in risk identification

**Deborah Mitchell (1989)** - Prospective Hindsight Study
- Demonstrated "prospective hindsight" improves prediction accuracy
- People identify more risks when imagining failure has occurred

**Daniel Kahneman** - "Thinking, Fast and Slow"
- Recommends pre-mortem for overcoming optimism bias
- Activates System 2 (analytical) thinking

### Psychological Mechanisms

1. **Overcomes Optimism Bias**: Natural tendency to underestimate risks
2. **Activates Prospective Hindsight**: "I knew it would fail because..."
3. **Makes Concerns Safe**: Not pessimism, but preparation
4. **Triggers System 2**: Slow, analytical thinking vs. fast intuition

## Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `analyze` | Run analysis with parameters | `analyze --project "X" --timeline "3m"` |
| `template` | Generate worksheet template | `template --format markdown` |
| `session` | Interactive guided session | `session` |

### Analyze Options
```
--project        Project name (required)
--description    Project description
--timeline       Project timeline (default: "3 months")
--stakeholders   Comma-separated stakeholder list
```

### Template Options
```
--format    Output format: markdown, json, text (default: markdown)
--output    Output file path (optional)
```

## Worksheet Template

The skill generates customizable worksheets:

### Markdown Template Includes:
- Project information section
- Failure path analysis (5 categories)
- Risk prioritization matrix
- Prevention action checklist
- Early warning indicators table
- Follow-up action items

### JSON Template:
For programmatic integration with project management tools.

## License

MIT License - See [LICENSE](LICENSE) file

## Contributing

Contributions welcome! Areas for enhancement:
- Additional risk pattern libraries
- Integration with PM tools (Jira, Linear)
- Visualization outputs (charts, graphs)
- Industry-specific risk templates

## References

1. Klein, G. (2007). Performing a Project Premortem. *Harvard Business Review*
2. Kahneman, D. (2011). *Thinking, Fast and Slow*
3. Mitchell, D. J., et al. (1989). The Effect of Imagining Future Events
4. Sibony, O. (2020). *You're About to Make a Terrible Mistake!*

---

**Remember**: "Fail to prepare, prepare to fail." The pre-mortem helps you prepare for failure so you can prevent it.
