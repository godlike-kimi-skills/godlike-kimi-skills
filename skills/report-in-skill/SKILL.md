# Report-In Skill

Generate comprehensive system status reports including completed tasks, running tasks, agent activities, memory usage, and port status.

## 何时使用本 Skill (Use When)

- Use this skill when you need a **daily status report** of all activities
- Use when checking **what tasks were completed** in the last 24 hours
- Use when monitoring **currently running tasks** and their progress
- Use when tracking **what other agents are working on**
- Use when checking **system memory usage** and resource consumption
- Use when verifying **port status** and network services
- Use when user mentions: `'report'`, `'status'`, `'what's happening'`, `'agent status'`, `'task progress'`, `'daily report'`, `'system status'`

## Out of Scope / 不适用范围

- **不提供远程服务器监控**（仅本地系统状态）
- **不修改系统配置**（仅读取和报告状态）
- **不管理或终止任务**（仅报告，不控制）
- **不替代专业监控工具**（如Prometheus、Zabbix）
- **不提供历史趋势分析**（仅当前状态和最近24小时）

如需远程监控，请使用 `prometheus-skill` 或 `grafana-skill`。

## Features

### 📊 Task Reports
- **Completed Tasks (24h)**: List of tasks finished in the last 24 hours with timestamps
- **Running Tasks**: Currently executing tasks with progress percentage
- **Task Statistics**: Success rate, average duration, task count by category

### 🤖 Agent Activities
- **Active Agents**: List of currently active agent processes
- **Agent Workloads**: What each agent is currently working on
- **Agent Performance**: CPU/memory usage per agent

### 💾 System Status
- **Memory Usage**: RAM usage, available memory, cache/buffers
- **Disk Usage**: Disk space by partition, usage percentages
- **CPU Usage**: Current load, process count

### 🌐 Network Status
- **Port Status**: Open ports, listening services
- **Network Connections**: Active connections by protocol
- **Service Health**: Status of common services (HTTP, SSH, DB, etc.)

## Usage Examples

### Generate Full Report
```bash
kimi skill report-in-skill report
```

### Check Tasks Only
```bash
kimi skill report-in-skill tasks
```

### Check Agent Activities
```bash
kimi skill report-in-skill agents
```

### Check Port Status
```bash
kimi skill report-in-skill ports
```

### Check Memory Usage
```bash
kimi skill report-in-skill memory
```

## Output Format

The skill generates a structured report like:

```
╔═══════════════════════════════════════════════════════════╗
║                    SYSTEM STATUS REPORT                    ║
║                    Generated: 2026-02-20 19:15:30         ║
╚═══════════════════════════════════════════════════════════╝

📊 TASK SUMMARY (Last 24 Hours)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Completed Tasks: 15
⏳ Running Tasks: 3
📈 Success Rate: 93%

Completed Tasks:
  ✓ skill-creator-enhanced ...... 2 hours ago
  ✓ docx-skill .................. 4 hours ago
  ✓ pdf-skill ................... 6 hours ago
  ...

Running Tasks:
  ⏳ batch-production ............ 45% complete
  ⏳ database-migration .......... 12% complete
  ⏳ model-training .............. 78% complete

🤖 AGENT ACTIVITIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Active Agents: 3

  🤖 Agent-A (PID: 12345)
     Status: Working on skill-creator
     CPU: 12% | Memory: 256MB
     Started: 2 hours ago

  🤖 Agent-B (PID: 12346)
     Status: Processing pdf-skill
     CPU: 8% | Memory: 128MB
     Started: 4 hours ago

💾 SYSTEM RESOURCES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Memory:
  Total: 16GB
  Used: 10.5GB (65%)
  Available: 5.5GB
  Cached: 2.1GB

Disk:
  /dev/sda1: 45% used (450GB/1TB)
  /dev/sdb1: 23% used (230GB/1TB)

CPU Load: 2.34 (4 cores)

🌐 PORT STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Active Services:
  ✓ 22/tcp   SSH ................... Listening
  ✓ 80/tcp   HTTP .................. Listening
  ✓ 443/tcp  HTTPS ................. Listening
  ✓ 5432/tcp PostgreSQL ............ Listening
  ✓ 6379/tcp Redis ................. Listening
  ✓ 8080/tcp Custom App ............ Listening

Total Open Ports: 12
Listening Services: 8
```

## Configuration

The skill can be configured via environment variables:

```bash
# Custom log paths
export REPORTIN_LOG_PATH="/var/log/custom"
export REPORTIN_TASK_LOG="/var/log/tasks.log"

# Report format (text/json/yaml)
export REPORTIN_FORMAT="text"

# Time range for completed tasks (hours)
export REPORTIN_TIME_RANGE=24
```

## Requirements

- Python 3.8+
- Windows/Linux/macOS support
- Access to system logs (read-only)
- psutil library for system metrics

## Technical Details

### Data Sources
- **Task Logs**: Reads from `~/.kimi/logs/tasks.log` or system task logs
- **Agent Status**: Scans running processes with "agent" or "kimi" in name
- **Memory Info**: Uses psutil library for cross-platform memory stats
- **Port Status**: Uses netstat/ss commands or psutil for network connections

### Performance
- Report generation: < 2 seconds
- Minimal CPU/memory overhead
- Read-only operations, no system modifications

## Troubleshooting

### No Task Data Found
Ensure task logging is enabled in your Kimi CLI configuration.

### Permission Denied
The skill requires read access to system logs and process information. Run with appropriate permissions.

### Incorrect Port Information
On some systems, netstat may require sudo. The skill will fallback to alternative methods.

## Integration

This skill can be combined with:
- `cron-skill` - Schedule daily reports
- `slack-mcp` - Send reports to Slack
- `email-mcp` - Email reports to stakeholders
- `markdown-docs-skill` - Generate formatted reports as documents

## License

MIT License - See LICENSE file
