# Report-In Skill 📊

Generate comprehensive system status reports including completed tasks, running tasks, agent activities, memory usage, and port status.

## Features ✨

- **📊 Task Reports**: View tasks completed in the last 24 hours and currently running tasks
- **🤖 Agent Monitoring**: Track what agents are doing and their resource usage
- **💾 System Metrics**: Monitor memory, disk, and CPU usage
- **🌐 Port Status**: Check open ports and listening services
- **📈 Progress Tracking**: View task completion percentages
- **🔔 Multiple Formats**: Text reports or JSON output

## Installation

```bash
# Clone the repository
git clone https://github.com/your-org/godlike-kimi-skills.git

# Install the skill
kimi skills install ./skills/report-in-skill

# Or install dependencies manually
pip install -r requirements.txt
```

## Quick Start

### Generate Full Report
```bash
kimi skill report-in-skill report
```

### Check Specific Areas
```bash
# View tasks only
kimi skill report-in-skill tasks

# Check agent activities
kimi skill report-in-skill agents

# View port status
kimi skill report-in-skill ports

# Check memory usage
kimi skill report-in-skill memory
```

### JSON Output
```bash
kimi skill report-in-skill report --json
```

## Usage Examples

### Daily Standup Report
```bash
kimi skill report-in-skill report
```

Output:
```
╔═══════════════════════════════════════════════════════════╗
║                    SYSTEM STATUS REPORT                    ║
║                    Generated: 2026-02-20 19:15:30         ║
╚═══════════════════════════════════════════════════════════╝

📊 TASK SUMMARY (Last 24 Hours)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Completed Tasks: 15
⏳ Running Tasks: 3

Completed Tasks:
  ✓ postgres-skill .............. 2 hours ago
  ✓ docker-skill ................ 4 hours ago
  ✓ kubernetes-skill ............ 6 hours ago
  ...

Running Tasks:
  ⏳ batch-production ............ [████████░░░░░░░░░░░░] 45%
  ⏳ database-migration .......... [██░░░░░░░░░░░░░░░░░░] 12%
  ⏳ model-training .............. [████████████████░░░░] 78%

🤖 AGENT ACTIVITIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Active Agents: 3

  🤖 agent-12345 (PID: 12345)
     Status: active
     Task: Working on skill-creator
     CPU: 12.0% | Memory: 256.0MB
     Uptime: 2h ago

💾 SYSTEM RESOURCES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Memory:
  Total: 16.0GB
  Used: 10.5GB (65.0%)
  Available: 5.5GB

Disk:
  ✓ /: 45% used (450GB/1TB)

🌐 PORT STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Active Services: 12

  ✓    22/tcp   SSH ................... Listening
  ✓    80/tcp   HTTP .................. Listening
  ✓   443/tcp   HTTPS ................. Listening
  ✓  5432/tcp   PostgreSQL ............ Listening
  ✓  6379/tcp   Redis ................. Listening
```

### Check Agent Status
```bash
kimi skill report-in-skill agents
```

```
🤖 AGENT ACTIVITIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Active Agents: 3

  🤖 agent-12345 (PID: 12345)
     Status: active
     CPU: 12.0% | Memory: 256.0MB
     Task: Working on skill-creator
     Uptime: 2h ago

  🤖 agent-12346 (PID: 12346)
     Status: active
     CPU: 8.0% | Memory: 128.0MB
     Task: Processing pdf-skill
     Uptime: 4h ago
```

### JSON API
```bash
kimi skill report-in-skill report --json | jq '.tasks.completed_24h'
```

```json
[
  {
    "name": "postgres-skill",
    "status": "completed",
    "end_time": "2026-02-20T17:15:30",
    "progress": 100.0
  },
  ...
]
```

## Configuration

Environment variables:

```bash
# Custom log paths
export REPORTIN_LOG_PATH="/var/log/custom"
export REPORTIN_TASK_LOG="tasks.log"

# Report format (text/json)
export REPORTIN_FORMAT="text"

# Time range for completed tasks (hours)
export REPORTIN_TIME_RANGE=24
```

## Command Reference

| Command | Description |
|---------|-------------|
| `report` | Generate full system report (default) |
| `tasks` | Show task summary |
| `agents` | Show agent activities |
| `ports` | Show port status |
| `memory` | Show memory and disk usage |
| `--json` | Output in JSON format |
| `--hours N` | Set time range for completed tasks |

## Integration

### Schedule Daily Reports
```bash
# Add to crontab for daily reports at 9 AM
0 9 * * * kimi skill report-in-skill report >> /var/log/daily-report.log
```

### Send to Slack
```bash
kimi skill report-in-skill report --json | kimi skill slack-skill send --channel "#daily-standup"
```

### Save as Markdown
```bash
kimi skill report-in-skill report > daily-report.md
```

## How It Works

### Data Sources
- **Task Logs**: Reads from `~/.kimi/logs/tasks.log`
- **Agent Status**: Scans running processes for agent patterns
- **Memory Info**: Uses psutil library or /proc/meminfo
- **Port Status**: Uses psutil or netstat command

### Progress Detection
- Analyzes file modification times for skill directories
- Reads .progress files if available
- Estimates progress based on task duration

## Requirements

- Python 3.8+
- psutil >= 5.9.0 (optional but recommended)
- Windows/Linux/macOS support

## Troubleshooting

### No Task Data
Ensure task logging is enabled in Kimi CLI configuration.

### Permission Denied
On Linux/macOS, some port information may require elevated permissions.

### Missing psutil
The skill works without psutil but with limited functionality:
```bash
pip install psutil
```

## Development

### Run Tests
```bash
cd skills/report-in-skill
python -m pytest test_skill.py -v
```

### Coverage Report
```bash
python -m pytest test_skill.py --cov=main --cov-report=html
```

## License

MIT License - See [LICENSE](LICENSE) file

## Contributing

Contributions welcome! Please follow the existing code style and add tests for new features.

## Support

For issues and feature requests, please use the GitHub issue tracker.
