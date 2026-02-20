---
name: net-debugger
version: 1.0
description: Network debugging tool with DNS resolution tracing, multi-node speed test, and route visualization.
---

# Net Debugger

Network diagnostics and DNS debugging for CLI.

## Features

- DNS resolution chain tracing
- Multi-node ping speed test
- TCP/ICMP dual-mode probing
- Route path visualization
- Port connectivity check

## Usage

```bash
# DNS check
python D:/kimi/skills/net-debugger/scripts/main.py dns-check github.com

# Ping test
python D:/kimi/skills/net-debugger/scripts/main.py ping 8.8.8.8

# Port check
python D:/kimi/skills/net-debugger/scripts/main.py port github.com 443

# Route trace
python D:/kimi/skills/net-debugger/scripts/main.py trace github.com
```
