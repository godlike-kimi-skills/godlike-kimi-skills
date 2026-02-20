---
name: container-doctor
version: 1.0
description: Docker/K8s container debugging with status monitoring, log analysis, and health checks.
---

# Container Doctor

Container diagnostics for Docker and Kubernetes.

## Features

- Docker container status monitoring
- Container log streaming and analysis
- Resource usage tracking (CPU/Memory/Network)
- Network isolation diagnostics
- Health check automation
- Image vulnerability scan

## Usage

```bash
# Check Docker status
python D:/kimi/skills/container-doctor/scripts/main.py status

# Container logs
python D:/kimi/skills/container-doctor/scripts/main.py logs container_name

# Resource stats
python D:/kimi/skills/container-doctor/scripts/main.py stats

# Health check
python D:/kimi/skills/container-doctor/scripts/main.py health
```
