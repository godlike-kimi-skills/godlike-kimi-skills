---
name: superpowers-review
description: "Use when completing tasks, implementing major features, or before merging to verify work meets requirements. Catches issues before they cascade."
---

# Code Review (Superpowers)

## Overview

Review early, review often. Catch issues before they compound.

## When to Request Review

**Mandatory:**
- After each task in development
- After completing major feature
- Before merge to main

**Optional but valuable:**
- When stuck (fresh perspective)
- Before refactoring (baseline check)
- After fixing complex bug

## How to Request

**1. Get git SHAs:**
```bash
BASE_SHA=$(git rev-parse HEAD~1)  # or origin/main
HEAD_SHA=$(git rev-parse HEAD)
```

**2. Review Checklist:**

Check against the plan:
- [ ] Implementation matches requirements
- [ ] Tests exist and pass
- [ ] No obvious bugs
- [ ] Code is readable
- [ ] No duplication
- [ ] Error handling present

**3. Severity Levels:**

- **Critical** - Blocks merge. Fix immediately.
- **Important** - Fix before proceeding
- **Minor** - Note for later

## Review Process

**What to check:**

1. **Correctness**
   - Does it do what the plan says?
   - Are edge cases handled?
   - Are errors handled?

2. **Test Coverage**
   - Tests exist?
   - Tests cover edge cases?
   - Tests actually test behavior (not mocks)?

3. **Code Quality**
   - Clear names?
   - Functions < 50 lines?
   - No duplication?
   - No magic numbers?

4. **TDD Compliance**
   - Tests written first?
   - Test fails correctly before implementation?

## Integration with Workflows

**After each task:**
- Review immediately
- Catch issues before they compound
- Fix before moving to next task

**After each batch (3 tasks):**
- Get feedback
- Apply fixes
- Continue

## Red Flags

**Never:**
- Skip review because "it's simple"
- Ignore Critical issues
- Proceed with unfixed Important issues

**If reviewer wrong:**
- Push back with technical reasoning
- Show code/tests that prove it works

$ARGUMENTS
