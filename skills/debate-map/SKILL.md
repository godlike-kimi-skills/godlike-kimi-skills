# Debate Map

**Source**: https://github.com/debate-map/app  
**Stars**: 8.2k+  
**Type**: Argument Visualization Platform  
**Description**: Restructuring dialogue into visual argument maps

---

## Overview

Debate Map transforms complex debates into **visual argument structures**. Instead of parsing walls of text, see claims, arguments, and their relationships at a glance.

**Website**: https://debatemap.app

---

## Core Structure

### Node Types

```
┌─────────────────────────────────────────┐
│              CLAIM (Gray)               │
│  "We should implement feature X"        │
└─────────────────────────────────────────┘
                    ↑
    ┌───────────────┴───────────────┐
    ↓                               ↓
┌──────────┐                  ┌──────────┐
│ ARGUMENT │                  │ ARGUMENT │
│  (Green) │                  │   (Red)  │
│ Supports │                  │ Opposes  │
└──────────┘                  └──────────┘
```

| Type | Color | Purpose | Example |
|------|-------|---------|---------|
| **Claim** | Gray | Statement to evaluate | "AI will replace programmers" |
| **Pro-argument** | Green | Supports claim | "GitHub Copilot already writes 30% of code" |
| **Con-argument** | Red | Opposes claim | "AI lacks architectural judgment" |

---

## Key Features

### 1. Two-Dimensional Structure
- **Vertical**: Levels of abstraction
- **Horizontal**: Competing arguments
- **Result**: See full landscape at once

### 2. Atomic Nodes
- Each node = one claim or one argument
- No compound statements
- Easy to evaluate individually

### 3. Rich Tools
- **Rating**: Vote on strength of arguments
- **Tagging**: Categorize by type
- **Statistical Analysis**: See consensus patterns
- **Belief Comparison**: Compare your view to others

---

## Argument Map Template

```
CENTRAL CLAIM:
[Main proposition to evaluate]

├─ SUPPORTING ARGUMENTS
│  ├─ [Argument 1]
│  │  └─ Evidence: [Source]
│  ├─ [Argument 2]
│  │  └─ Evidence: [Source]
│  └─ [Argument 3]
│     └─ Evidence: [Source]
│
└─ OPPOSING ARGUMENTS
   ├─ [Counter-argument 1]
   │  └─ Evidence: [Source]
   ├─ [Counter-argument 2]
   │  └─ Evidence: [Source]
   └─ [Counter-argument 3]
      └─ Evidence: [Source]

REBUTTALS:
├─ [Rebuttal to opp-1]
└─ [Rebuttal to opp-2]

UNCERTAINTY:
├─ [What we don't know]
└─ [Key assumptions]
```

---

## Kbot Application: Decision Mapping

### Use Case: Pivot Decision

```
CLAIM: "We should pivot from B2C to B2B"

SUPPORTING (Green):
├─ "B2C CAC is $150, LTV is $80" [Financial unsustainable]
├─ "3 B2B prospects have requested demos" [Validating demand]
└─ "B2B sales cycle is shorter in our network" [Speed to revenue]

OPPOSING (Red):
├─ "We've invested 6 months in B2C product" [Sunk cost]
├─ "B2B requires features we don't have" [Technical debt]
└─ "No B2B experience on team" [Execution risk]

REBUTTALS:
├─ "Sunk cost is irrelevant to future value"
└─ "Features can be built in 2 weeks"

CONFIDENCE: 75% (strong support, manageable opposition)
DECISION: Proceed with pivot
```

### Use Case: Feature Prioritization

```
CLAIM: "Should we build feature X?"

PRO:
├─ "Users requested it 15 times" [Demand signal]
├─ "Competitor has it" [Competitive parity]
└─ "Enables premium pricing" [Revenue impact]

CON:
├─ "Will take 4 weeks" [Opportunity cost]
├─ "Only 5% of users would use it" [Limited impact]
└─ "Workaround exists" [Lower priority]

ANALYSIS: Low impact / High cost = Deprioritize
```

---

## Mapping Protocol

### Step 1: Identify the Central Claim
What's the core proposition? Make it specific and falsifiable.

### Step 2: Brainstorm All Arguments
Don't filter yet. List everything for and against.

### Step 3: Organize into Tree
Group related arguments. Create hierarchy if needed.

### Step 4: Assess Strength
Rate each argument (strong/moderate/weak).

### Step 5: Identify Gaps
What's missing? What would change your mind?

### Step 6: Decide
Based on map, what's the balance of evidence?

---

## Visual Notation

```
[+] Strong argument (solid line)
[±] Moderate argument (dashed line)
[-] Weak argument (dotted line)

→ Direct support
⇒ Conditional support ("if X then Y")
⊸ Partial support (one of many factors)
```

---

## Integration with Kbot

### /map command
```
/map "Should we kill this project?"

Output:
├─ Generates structured argument map
├─ Identifies hidden assumptions  
└─ Suggests evidence to gather
```

### Decision Reviews
Every major decision gets a debate map before finalizing.

### Team Alignment
Share maps to ensure everyone's concerns are captured.

---

*Visual reasoning for complex decisions.*
