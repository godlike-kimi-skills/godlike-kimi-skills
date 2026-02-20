---
name: system-monitor
version: 2.2
description: System resource monitoring with Windows protection, circuit breaker pattern, and agent spawn validation.
---

# System Monitor v2.2

**System resource monitoring with enhanced protection and predictive warnings.**

## What's New in v2.2
- Added predictive resource exhaustion warnings
- Enhanced circuit breaker pattern for agent spawning
- Added GPU monitoring support for future ML workloads

## System Reserve - Protected for Windows Stability

```python
SYSTEM_RESERVE = {
    "cpu_cores": 4,      # 25% of 16 cores
    "memory_gb": 8,      # 25% of 32GB
    "description": "Reserved for Windows OS and base applications"
}
```

## Usage

### Check System Status

```bash
python D:/kimi/skills/system-monitor/scripts/monitor.py status
```

### Check if Can Spawn Subagent

```bash
python D:/kimi/skills/system-monitor/scripts/monitor.py can-spawn
# Returns: YES/NO with reason
```

### Continuous Monitoring

```bash
python D:/kimi/skills/system-monitor/scripts/monitor.py watch --interval 30
```

### Circuit Breaker Operations

```bash
# Check circuit breaker status
python D:/kimi/skills/system-monitor/scripts/monitor.py circuit-status

# Reset circuit breaker (after issue resolved)
python D:/kimi/skills/system-monitor/scripts/monitor.py circuit-reset

# Manually trip circuit (emergency stop)
python D:/kimi/skills/system-monitor/scripts/monitor.py circuit-trip
```

## Concurrency Rules

```python
MAX_CONCURRENT_AGENTS = 12  # 16 cores - 4 reserved
MAX_AGENT_MEMORY_GB = 2     # Per agent limit
```

## Memory Thresholds (Based on 32GB Total, 8GB Reserved)

| Threshold | System Usage | Status |
|-----------|-------------|--------|
| Healthy | < 8GB (25%) | 🟢 |
| Normal | 8-16GB (25-50%) | 🟡 |
| Warning | 16-24GB (50-75%) | 🟠 |
| Danger | > 24GB (>75%) | 🔴 |
| Critical | > 28GB (>87%) | 🚨 |

## CPU Thresholds (Based on 16 Cores, 4 Reserved)

| Threshold | Core Usage | Status |
|-----------|-----------|--------|
| Healthy | < 4 cores (25%) | 🟢 |
| Normal | 4-8 cores (25-50%) | 🟡 |
| Warning | 8-12 cores (50-75%) | 🟠 |
| Danger | > 12 cores (>75%) | 🔴 |
| Critical | > 14 cores (>87%) | 🚨 |

## Circuit Breaker States

- **CLOSED**: Normal operation, agents can spawn
- **OPEN**: Too many failures, blocking new spawns
- **HALF-OPEN**: Testing if system recovered

## Integration

### In Agent Spawner

```python
from system_monitor import check_can_spawn

can_spawn, reason = check_can_spawn()
if can_spawn:
    spawn_subagent(task)
else:
    queue_task(task)  # Wait for resources
```

### Health Check

```bash
python D:/kimi/skills/system-monitor/scripts/monitor.py health-check
```

## Best Practices

- ✅ Always reserve 25% for system (Windows)
- ✅ Use per-agent memory caps (2GB)
- ✅ Monitor swap usage, not just RAM
- ✅ Set up alerts at Warning threshold
- ✅ Implement graceful degradation

## Configuration

Edit `D:/kimi/kbot-data/config.toml`:

```toml
[system_monitor]
enabled = true
auto_check_interval = 30
alert_on_warning = true
stop_on_danger = true
max_agent_memory_gb = 2
```
