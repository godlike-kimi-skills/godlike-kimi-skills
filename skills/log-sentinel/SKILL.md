---
name: log-sentinel
version: 1.0
description: Real-time log monitoring with keyword highlighting, pattern matching, and cross-platform audio alarms.
---

# Log Sentinel

Real-time log file monitoring with audio alerts.

## Features

- Real-time log file/directory monitoring
- Keyword matching with highlight (ERROR/CRITICAL/FATAL/超时/连接失败)
- Cross-platform audio alarm (Windows/Linux/macOS)
- Multiple log file support
- Configurable alert patterns
- Filter and ignore rules

## Usage

```bash
# Monitor single file
python D:/kimi/skills/log-sentinel/scripts/main.py monitor D:/kimi/logs/wake-up.log

# Monitor directory
python D:/kimi/skills/log-sentinel/scripts/main.py monitor D:/kimi/logs --pattern "*.log"

# Monitor with alert
python D:/kimi/skills/log-sentinel/scripts/main.py monitor D:/kimi/logs --alert

# Configuration
python D:/kimi/skills/log-sentinel/scripts/main.py config --path "D:/kimi/logs" --keywords "ERROR,CRITICAL"
```

## Configuration

```toml
[log-sentinel]
monitor_path = "D:/kimi/logs"
pattern = "*.log"
keywords = ["ERROR", "CRITICAL", "FATAL", "超时", "连接失败"]
audio_alarm = true
alarm_file = "alarm.wav"
```
