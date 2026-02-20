---
name: debug-master
version: 1.0
description: Advanced debugging tool for CLI with PDB/WinDbg integration, breakpoint capture, and stack trace analysis.
---

# Debug Master

Advanced debugging tool for Kimi CLI with multi-platform support.

## Features

- PDB integration for Python debugging
- WinDbg support for Windows system debugging
- Breakpoint capture and management
- Variable tracing and inspection
- Stack trace export and analysis
- CLI error code auto-parse

## Usage

```bash
# Test mode
python D:/kimi/skills/debug-master/scripts/main.py --test

# Debug a Python script
python D:/kimi/skills/debug-master/scripts/main.py debug script.py

# Analyze error code
python D:/kimi/skills/debug-master/scripts/main.py error 0x80070005
```
