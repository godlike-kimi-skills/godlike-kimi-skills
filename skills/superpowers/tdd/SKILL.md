---
name: superpowers-tdd
description: "MUST use when implementing any feature or bugfix, before writing implementation code. Enforces RED-GREEN-REFACTOR cycle."
---

# Test-Driven Development (Superpowers)

## Overview

**Core principle:** Write the test first. Watch it fail. Write minimal code to pass.

**Iron Law:**
```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Write code before the test? **Delete it. Start over.**

## When to Use

**Always:**
- New features
- Bug fixes
- Refactoring
- Behavior changes

**Exceptions** (ask your human partner):
- Throwaway prototypes
- Generated code
- Configuration files

## Red-Green-Refactor Cycle

### RED - Write Failing Test

Write one minimal test showing what should happen.

**Requirements:**
- One behavior per test
- Clear name (no "test1", "it works")
- Real code (no mocks unless unavoidable)

**Example (Good):**
```python
def test_retries_failed_operations_3_times():
    attempts = 0
    def operation():
        attempts += 1
        if attempts < 3:
            raise Error('fail')
        return 'success'
    
    result = retry_operation(operation)
    
    assert result == 'success'
    assert attempts == 3
```

### Verify RED - Watch It Fail

**MANDATORY. Never skip.**

```bash
# Python
pytest path/to/test.py -v

# JavaScript
npm test path/to/test.test.ts
```

Confirm:
- Test fails (not errors)
- Failure message is expected
- Fails because feature missing

**Test passes?** You're testing existing behavior. Fix test.

### GREEN - Minimal Code

Write simplest code to pass the test.

**Example:**
```python
async def retry_operation(fn):
    for i in range(3):
        try:
            return await fn()
        except:
            if i == 2:
                raise
```

Don't add features, refactor, or "improve" beyond the test.

### Verify GREEN - Watch It Pass

**MANDATORY.**

Run tests again. Confirm:
- Test passes
- Other tests still pass
- No errors/warnings

### REFACTOR - Clean Up

After green only:
- Remove duplication
- Improve names
- Extract helpers

Keep tests green. Don't add behavior.

## Red Flags - STOP and Start Over

- Code before test
- Test after implementation
- Test passes immediately
- "I'll write tests after"
- "Keep as reference" (delete means delete)
- "TDD is dogmatic, I'm being pragmatic"

**All of these mean: Delete code. Start over with TDD.**

## Common Rationalizations (and Why They're Wrong)

| Excuse | Reality |
|--------|---------|
| "Too simple to test" | Simple code breaks. Test takes 30 seconds. |
| "I'll test after" | Tests passing immediately prove nothing. |
| "Deleting X hours is wasteful" | Sunk cost. Keeping unverified code is debt. |
| "Already manually tested" | Ad-hoc ≠ systematic. Can't re-run. |
| "TDD will slow me down" | TDD faster than debugging production. |

$ARGUMENTS
