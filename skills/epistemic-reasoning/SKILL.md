# Epistemic Reasoning

**Source**: epistemic-me (philosophical framework)  
**Stars**: 5.7k+ (estimated)  
**Type**: Philosophical Framework  
**Description**: Epistemology + Bayesian belief modeling for rigorous thinking

---

## Core Concepts

### Epistemology
The study of knowledge, belief, and justification. Questions we ask:
- What can we know?
- How do we know it?
- What is the nature of belief?

### Bayesian Belief Modeling
Representing beliefs as probability distributions that update with evidence.

```
Belief State = {Hypothesis, Prior Probability, Evidence History}
```

---

## The Epistemic Stack

```
Level 5: Actions (what we do)
Level 4: Decisions (what we choose)
Level 3: Beliefs (what we think is true)
Level 2: Evidence (what we observe)
Level 1: Reality (what actually is)
```

**Key insight**: Quality at each level affects all levels above.

---

## Belief Calibration

### The Calibration Game
1. Make 100 predictions at 90% confidence
2. If calibrated, 90 should be correct
3. Track and adjust

### Common Miscalibrations

| Pattern | Symptom | Fix |
|---------|---------|-----|
| Overconfidence | 90% predictions, 60% correct | Widen confidence intervals |
| Underconfidence | 50% predictions, 80% correct | Narrow confidence intervals |
| Poor discrimination | Can't tell easy from hard | Practice with feedback |

---

## Epistemic Virtues

### 1. Accuracy
- **Goal**: Beliefs match reality
- **Practice**: Seek truth, not confirmation

### 2. Calibration
- **Goal**: Confidence matches accuracy
- **Practice**: Track predictions, update

### 3. Coherence
- **Goal**: Beliefs don't contradict
- **Practice**: Bayesian updating, consistency checks

### 4. Openness
- **Goal**: Update on new evidence
- **Practice**: Pre-mortems, red teaming

### 5. Humility
- **Goal**: Appropriate confidence levels
- **Practice**: Base rates, outside view

---

## Belief Update Protocol

```
INITIAL BELIEF:
- Hypothesis: [Statement]
- Prior: [0-100%]
- Key assumptions: [List]

NEW EVIDENCE:
- Observation: [What happened]
- Likelihood if true: [P(E|H)]
- Likelihood if false: [P(E|¬H)]
- Bayes Factor: [Ratio]

UPDATED BELIEF:
- Posterior: [New probability]
- Confidence change: [Delta]
- Action threshold crossed? [Yes/No]
```

---

## Application: Kbot Decision Making

### Project Evaluation
```
Hypothesis: "This project will generate $1000/month"

Prior (base rate of similar projects): 15%

Evidence Phase 1 (MVP built):
- P(E|Success) = 80% (most successful projects built MVP)
- P(E|Failure) = 40% (some failed projects also built MVP)
- Bayes Factor = 2
- Posterior = 15% × 2 = 26%

Evidence Phase 2 (First customer):
- P(E|Success) = 90%
- P(E|Failure) = 10%
- Bayes Factor = 9
- Posterior = 26% × 9 = 70% → Proceed threshold reached
```

### Kill Criteria as Belief Thresholds
```
Kill if P(Success) < 30%
Pivot if 30% < P(Success) < 70%
Scale if P(Success) > 70%
```

---

## Epistemic Hazards

| Hazard | Warning Sign | Defense |
|--------|-------------|---------|
| Motivated reasoning | Wanting it to be true | Pre-commit to criteria |
| Confirmation bias | Seeking supporting evidence | Active disconfirmation |
| Anchoring | First number dominates | Multiple anchors |
| Availability bias | Vivid examples overweight | Base rates |
| Sunk cost | Past investment influences | Evaluate marginal value |

---

## The Outside View

When evaluating a project:
1. **Inside view**: Details of this specific case
2. **Outside view**: Base rate of similar cases

**Rule**: Always start with outside view, then adjust.

---

*"The first principle is that you must not fool yourself — and you are the easiest person to fool."* — Richard Feynman
