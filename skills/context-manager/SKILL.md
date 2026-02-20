---
name: context-manager
version: 2.1
description: LLM context window management with AUTO-HANDOFF. Automatically triggers phase handoff when context reaches threshold. No prompts, just execution.
---

# Context Manager v2.1 - Auto-Handoff

**Automatic Phase Handoff when context threshold is reached.**

## What's New in v2.1
- Added token prediction using sliding window analysis
- Improved smart context compression for code blocks
- Added support for multi-phase handoff with checkpoints

## Auto-Handoff Threshold

```
AUTO_HANDOFF_THRESHOLD = 80,000 tokens
```

**Why 80K?**
- Below 50K: Safe zone (94% success rate)
- 50K-80K: Warning zone (81% success rate)  
- 80K+: Auto-handoff triggered (preserves 64%+ success rate)

## Usage

### Auto Mode (Recommended)

```bash
# Enable auto-handoff monitoring
python D:/kimi/skills/context-manager/scripts/context.py auto-on

# Record context - will auto-handoff if >= 80K
python D:/kimi/skills/context-manager/scripts/context.py record 75000

# Check auto-handoff status
python D:/kimi/skills/context-manager/scripts/context.py auto-status

# Disable auto-handoff
python D:/kimi/skills/context-manager/scripts/context.py auto-off
```

### Manual Commands

```bash
# Force immediate handoff
python D:/kimi/skills/context-manager/scripts/context.py handoff-now \
  --from-phase "analysis" \
  --to-phase "implementation"

# Check if should handoff (returns exit code)
python D:/kimi/skills/context-manager/scripts/context.py should-handoff
# Exit 0 = should handoff, Exit 1 = continue

# Get current context size
python D:/kimi/skills/context-manager/scripts/context.py current
```

## Auto-Handoff Behavior

When context >= 80K tokens:

1. **IMMEDIATE**: No prompt, no confirmation
2. **CONTEXT FOLDING**:
   - Clear: Tool outputs, intermediate calculations, temp files
   - Preserve: Key findings, decisions, code artifacts, user requirements
3. **SPAWN NEW AGENT**: Fresh 0K context
4. **CONTINUE**: Next phase with compact context (~5-10K)

## Integration

### In Agent Workflow

```python
# Before each major operation:
1. Check current context
2. If >= 80K: AUTO_HANDOFF()
3. Else: Continue operation
```

### With Task Tracker

```bash
# When task switches phase, check context
python D:/kimi/skills/context-manager/scripts/context.py check-and-handoff \
  --current-phase "design" \
  --next-phase "coding"
```

## Threshold Configuration

Edit `D:/kimi/kbot-data/config.toml`:

```toml
[context_manager]
auto_handoff_enabled = true
auto_handoff_threshold = 80000  # 80K tokens
preserve_artifacts = ["*.json", "*.md", "decisions/*"]
```

## No-Reminder Policy

**This skill does NOT:**
- ❌ Ask for confirmation
- ❌ Show warnings and wait
- ❌ Suggest actions

**This skill DOES:**
- ✅ Monitor context automatically
- ✅ Execute handoff at threshold
- ✅ Log all transitions
- ✅ Preserve critical artifacts

**Just set it and forget it.**
