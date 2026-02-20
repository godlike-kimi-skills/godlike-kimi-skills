# Code Quality Metrics Guide

## Table of Contents
1. [Cyclomatic Complexity](#complexity)
2. [Line Metrics](#lines)
3. [Duplicate Detection](#duplicates)
4. [Maintainability Index](#maintainability)
5. [Quality Score](#quality)
6. [Best Practices](#best-practices)

## Cyclomatic Complexity <a name="complexity"></a>

### Definition
Measures the number of linearly independent paths through code.

### Calculation
- Base complexity: 1
- +1 for each `if`, `while`, `for`, `except`
- +1 for each boolean operator (`and`, `or`)
- +1 for each `case` in switch/match

### Classifications
| Level | Complexity | Recommendation |
|-------|-----------|----------------|
| Low | 1-5 | ✓ Acceptable |
| Medium | 6-10 | ⚠ Review |
| High | 11-20 | ⚠ Refactor |
| Very High | 21+ | ❌ Immediate attention |

### Example
```python
def simple():              # Complexity: 1
    return 1

def medium(x):             # Complexity: 3
    if x > 0:              # +1
        return 1
    elif x < 0:            # +1
        return -1
    else:                  # +1
        return 0

def complex(a, b):         # Complexity: 5
    if a > 0:              # +1
        if b > 0:          # +1
            return 1
        return 2           # implicit else
    elif a < 0:            # +1
        return 3 if b > 0 else 4  # +1 for ternary
    return 5               # +1
```

## Line Metrics <a name="lines"></a>

### Types
| Type | Description |
|------|-------------|
| Total | All lines in file |
| Code | Executable lines (excluding comments/blanks) |
| Blank | Empty lines |
| Comment | `#` comment lines |
| Docstring | `"""docstring"""` lines |

### Comment Ratio
```
Comment Ratio = (Comment + Docstring) / Code × 100%
```

### Recommended Ratios
- **Low** (< 10%): Add more documentation
- **Good** (10-30%): Balanced
- **High** (> 30%): May indicate over-commenting

## Duplicate Detection <a name="duplicates"></a>

### Method
1. Normalize code (lowercase, remove whitespace/comments)
2. Create sliding windows of N lines
3. Hash each window
4. Compare hashes across files

### Configuration
```python
min_duplicate_lines = 5  # Minimum lines to consider
```

### Duplicate Types
| Type | Example | Action |
|------|---------|--------|
| Exact | Copy-pasted code | Extract function |
| Near-miss | Similar with small changes | Refactor with parameters |
| Structural | Same pattern, different data | Use abstraction |

## Maintainability Index <a name="maintainability"></a>

### Calculation
```
MI = 100 - (Average Complexity × 2)
     - max(0, 20 - Comment Ratio)
     - (Code Lines / 100)
```

### Interpretation
| Score | Rating |
|-------|--------|
| 85-100 | Excellent |
| 70-84 | Good |
| 50-69 | Fair |
| 0-49 | Poor |

## Quality Score <a name="quality"></a>

### Factors

#### Positive Factors
- Good comment ratio (+5)
- Low complexity (+10)
- No duplicates (+15)
- Reasonable file size (+5)

#### Negative Factors
- High complexity functions (-5 each)
- Duplicate blocks (-10 each)
- Large files >500 lines (-10)
- Large files >1000 lines (-20)
- Low comment ratio <10% (-10)

### Formula
```
Base Score = 100
+ Positive Factors
- Negative Factors
× Maintainability Factor
= Final Score (0-100)
```

## Best Practices <a name="best-practices"></a>

### Reducing Complexity
1. **Extract functions**: Break large functions into smaller ones
2. **Use early returns**: Reduce nesting
3. **Simplify conditionals**: Use lookup tables for complex switches
4. **Apply polymorphism**: Replace conditionals with inheritance

```python
# Before: High complexity
def process(data, type):
    if type == 'A':
        if data.valid:
            return process_a(data)
        else:
            return None
    elif type == 'B':
        # ... more nested conditions

# After: Lower complexity
def process(data, type):
    if not data.valid:
        return None
    
    processors = {
        'A': process_a,
        'B': process_b,
    }
    return processors.get(type, default_process)(data)
```

### Eliminating Duplicates
1. **Extract common code** into functions
2. **Use inheritance** for shared behavior
3. **Apply template method** pattern
4. **Create utility modules** for repeated operations

### Improving Maintainability
1. **Write docstrings** for all public functions
2. **Add inline comments** for complex logic
3. **Keep functions small** (< 50 lines)
4. **Keep files small** (< 500 lines)
5. **Use descriptive names**

### Code Review Checklist
- [ ] Complexity < 10 for all functions
- [ ] No duplicate code blocks
- [ ] Comment ratio 10-30%
- [ ] File size < 500 lines
- [ ] Maintainability index > 70

### CI/CD Integration
```yaml
# .github/workflows/code-quality.yml
- name: Check Code Metrics
  run: |
    python -m scripts.main . --format json --output metrics.json
    QUALITY=$(jq '.summary.quality_score' metrics.json)
    if (( $(echo "$QUALITY < 70" | bc -l) )); then
      echo "Quality score $QUALITY is below threshold"
      exit 1
    fi
```

### Trending
Track metrics over time to identify:
- **Improving areas**: Focus of refactoring efforts
- **Degrading areas**: Need immediate attention
- **Stable areas**: Maintain current practices

```python
# Compare with baseline
if current.quality_score < baseline.quality_score * 0.95:
    alert("Quality regression detected!")
```
