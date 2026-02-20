# Loopy Systems

**Source**: ncase.me/loopy (concept)  
**Stars**: 6.9k+ (estimated)  
**Type**: System Dynamics Tool  
**Description**: Systems dynamics and causal loop modeling

---

## Overview

Loopy is a tool for thinking in **systems**. It helps you create causal loop diagrams to understand how complex systems work, where leverage points are, and what interventions might work.

---

## Core Concepts

### Stocks and Flows

**Stocks**: Accumulations (the "bathtubs")
- User base, revenue, inventory, reputation
- Change slowly, have memory

**Flows**: Rates of change (the "faucets and drains")
- New users/day, churn rate, spend rate
- Can change quickly

```
         Inflow                    Outflow
            ↓                         ↓
    ┌───────────────┐         ┌───────────────┐
    │    STOCK      │  →  →   │    STOCK      │
    │  (User Base)  │         │  (Revenue)    │
    └───────────────┘         └───────────────┘
            ↓
       Conversion
```

### Feedback Loops

#### Reinforcing Loops (R)
Amplify change — virtuous or vicious cycles.

```
    More Users
        ↓
   More Network Value
        ↓
   More User Acquisition
        ↓
    More Users (R)
```

**Examples**:
- Viral growth
- Compound interest
- Arms races

#### Balancing Loops (B)
Stabilize systems — seek equilibrium.

```
    Revenue Growth
        ↓
   Increased Competition
        ↓
   Market Share Pressure
        ↓
   Revenue Stabilization (B)
```

**Examples**:
- Thermostat regulation
- Market saturation
- Resource limits

### Delays
Time lags between cause and effect.

```
    Marketing Spend
        ↓ [delay]
    Brand Awareness
        ↓ [delay]
    Customer Acquisition
```

**Danger**: Delays cause oscillation and instability.

---

## Causal Loop Diagram Notation

```
[A] ──(+)>── [B]    A increases → B increases
[A] ──(-)>── [B]    A increases → B decreases

(+): Reinforcing relationship
(-): Balancing relationship

R: Reinforcing loop (amplifies)
B: Balancing loop (stabilizes)
```

---

## Kbot Business Model as System

### Complete System Map

```
                    ┌─────────────────┐
                    │   Marketing     │
                    │     Spend       │
                    └────────┬────────┘
                             │(+)
                             ↓
┌──────────┐(+)
┌──────────┐(+)
┌──────────┐(+)
│  User    │─────────>│  Revenue   │
│  Growth  │          │   Growth   │
│   (R1)   │          │    (R2)    │
└──────────┘          └────────────┘
     ↑                     │
     │(+)
┌────┴────┐               │(+)
│ Network │               ↓
│ Effects │        ┌──────────────┐
└─────────┘        │  Kimi Token  │
                   │   Budget     │
                   └──────┬───────┘
                          │(+)
                          ↓
                   ┌──────────────┐
                   │  Capability  │
                   │  Expansion   │
                   └──────────────┘

BALANCING FORCES:
                    ┌─────────────────┐
                    │   Market Sat.   │
                    │     (B1)        │
                    └─────────────────┘

                    ┌─────────────────┐
                    │   Cost Growth   │
                    │     (B2)        │
                    └─────────────────┘
```

### Loop Analysis

**R1 - Viral Growth Loop**
```
Users → Network Value → Referrals → New Users → Users
```
- Type: Reinforcing
- Effect: Growth acceleration
- Leverage: Viral coefficient

**R2 - Reinvestment Loop**
```
Revenue → Kimi Budget → Capability → Better Product → Revenue
```
- Type: Reinforcing  
- Effect: Compound improvement
- Leverage: Token efficiency

**B1 - Market Saturation**
```
Market Share → Remaining Market → Growth Rate → Market Share
```
- Type: Balancing
- Effect: Growth ceiling
- Leverage: New markets

**B2 - Cost Constraint**
```
Revenue → Costs → Margin Pressure → Efficiency Focus
```
- Type: Balancing
- Effect: Profitability enforcement
- Leverage: Automation

---

## System Archetypes

### 1. Limits to Growth
Growth hits a ceiling.

```
    Growth ──(+)>── Performance
      ↑                  │
      │                  ↓(-)
      └───────── [Limit]
```

**Strategy**: Identify and break the limit.

### 2. Shifting the Burden
Quick fix undermines fundamental solution.

```
    Problem ──(+)>── Symptom Fix
      │                  │
      │                  ↓(-)
      └───────── [Fundamental Solution]
```

**Strategy**: Invest in fundamentals despite delay.

### 3. Tragedy of the Commons
Individual rationality → collective disaster.

```
    Individual Benefit ──(+)>── Activity
                                    │
                                    ↓(+)
                              Resource Depletion
                                    │
                                    ↓(-)
                            Individual Benefit
```

**Strategy**: Shared governance mechanisms.

### 4. Success to the Successful
Winners get resources to win more.

```
    Success ──(+)>── Resources ──(+)>── Success
      │                                         │
      └─────────────── [Competitor] <───────────┘
```

**Strategy**: Diversify or create separate pools.

---

## Leverage Points

Where small changes produce big results (in order of effectiveness):

| Rank | Intervention | Example |
|------|--------------|---------|
| 1 | Paradigm/ mindset | "Revenue = bad metric" |
| 2 | System goal | Change from growth to profit |
| 3 | Information flow | Real-time dashboards |
| 4 | Self-organization | Team autonomy |
| 5 | Rules/incentives | Compensation structure |
| 6 | Information | Market data |
| 7 | Feedback delays | Reduce reporting lag |
| 8 | Stocks | Cash reserves |
| 9 | Parameters | Prices, rates |

---

## Kbot Application

### /system command
```
/system "analyze my business model"

Output:
├─ Identifies all feedback loops
├─ Maps stocks and flows
├─ Finds leverage points
└─ Suggests interventions
```

### Growth Strategy
```
Map current growth loops:
1. Identify reinforcing loops
2. Strengthen them
3. Identify limiting loops
4. Break or weaken them
```

### Risk Analysis
```
Map failure modes:
1. What loops could reverse?
2. Where are delays hiding problems?
3. What stocks are too low?
4. What flows are unbalanced?
```

---

*Think in loops, not lines.*
