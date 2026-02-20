# Logikon Audit

**Source**: https://github.com/logikon-ai/logikon  
**Stars**: 3.1k+  
**Type**: LLM Analytics Tool  
**Description**: Analyzing and scoring reasoning traces of LLMs

---

## Overview

Logikon provides **AI Analytics for Natural Language Reasoning**. It evaluates the quality of arguments and reasoning produced by LLMs (and humans).

---

## Core Features

### 1. Argument Extraction
Automatically identifies:
- **Claims** (conclusions)
- **Premises** (supporting statements)
- **Inference patterns** (how premises support claims)

### 2. Reasoning Quality Scoring
Evaluates reasoning on multiple dimensions:
- **Validity**: Does the conclusion follow from premises?
- **Soundness**: Are premises actually true?
- **Completeness**: Are all relevant factors considered?
- **Coherence**: Do all parts fit together?

### 3. Guided Reasoning™
Structured process for walking AI agents through complex reasoning:
```
User Problem → Guide LLM → Instructions → Client LLM → Reasoning → Evaluation → Answer
```

---

## Scoring Dimensions

### Argument Structure
| Criterion | Question | Score |
|-----------|----------|-------|
| Claim clarity | Is the conclusion clear? | 0-10 |
| Premise support | Do premises support the claim? | 0-10 |
| Inference validity | Is the reasoning valid? | 0-10 |
| Alternative coverage | Are alternatives considered? | 0-10 |

### Reasoning Quality
| Criterion | Question | Score |
|-----------|----------|-------|
| Evidence quality | How strong is the evidence? | 0-10 |
| Bias awareness | Does it acknowledge biases? | 0-10 |
| Uncertainty calibration | Is confidence appropriate? | 0-10 |
| Actionability | Does it lead to clear action? | 0-10 |

---

## Kbot Application: Reasoning Audit

### Use Case 1: Decision Validation
```
Decision: "Should we pivot this project?"

Logikon Analysis:
├─ Claim: "We should pivot"
├─ Premise 1: "Revenue is below target" [Strong evidence]
├─ Premise 2: "Market feedback is negative" [Moderate evidence]
├─ Premise 3: "Competitors are ahead" [Weak evidence - unverified]
└─ Missing: Cost of pivot, alternative strategies

Score: 6.5/10 - Decision supported but incomplete
Recommendation: Gather competitor intelligence before deciding
```

### Use Case 2: Argument Mapping
```
Issue: "Should I eat animals?"
Reasoning: "No! Animals can suffer. Animal farming causes climate heating."

Logikon Map:
├─ Main Claim: "Should not eat animals"
├─ Argument 1 (Ethical)
│  └─ Premise: "Animals can suffer"
│     └─ Supports: Main Claim
├─ Argument 2 (Environmental)
│  └─ Premise: "Farming causes climate heating"
│     └─ Supports: Main Claim
└─ Missing Arguments
   ├─ Health considerations?
   ├─ Economic impacts?
   └─ Cultural factors?
```

### Use Case 3: Bias Detection
```
Reasoning Audit:
├─ Detected: Confirmation bias
│  └─ Only seeking supporting evidence
├─ Detected: Availability heuristic
│  └─ Overweighting recent examples
└─ Recommendation
   └─ Apply red team protocol
```

---

## Audit Checklist

Before finalizing any decision:

- [ ] **Claim is explicit**: What exactly are we deciding?
- [ ] **Premises identified**: What supports this conclusion?
- [ ] **Evidence assessed**: How strong is each premise?
- [ ] **Alternatives considered**: What else could we do?
- [ ] **Biases checked**: Common fallacies avoided?
- [ ] **Confidence calibrated**: Is certainty level appropriate?
- [ ] **Action clear**: What happens next?

---

## Quick Audit Commands

```
/audit "[decision text]"
→ Returns: Structure score, bias check, recommendations

/map "[argument text]"  
→ Returns: Visual argument map

/score "[reasoning text]"
→ Returns: Quality scores across dimensions
```

---

## Integration with Kbot Workflow

### Stage 1: Pre-Launch
- Audit business model assumptions
- Validate market hypothesis reasoning

### Stage 2: Validation
- Score 10-minute checkpoint logic
- Check for premature conclusions

### Stage 3: Pivot/Kill
- Audit decision to pivot
- Validate kill criteria application

### Stage 4: Scale
- Score expansion reasoning
- Check for overconfidence

---

*Every reasoning trace can be improved through systematic analysis.*
