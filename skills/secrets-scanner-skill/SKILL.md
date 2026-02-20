# Secrets Scanner Skill

Automated sensitive information scanner for API keys, passwords, tokens, and secrets. Use when auditing code security, scanning for vulnerabilities, or when user mentions 'security', 'vulnerability', 'CVE'.

## Features

- **Multi-pattern detection**: API keys, passwords, tokens, certificates
- **Git history scanning**: Find secrets in commit history
- **Entropy analysis**: Detect high-entropy strings
- **False positive filtering**: Reduce noise with smart filtering

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Command Line

```bash
# Scan current directory
python scripts/main.py --target ./my-project

# Scan with git history
python scripts/main.py --target ./my-project --scan-history

# Scan specific file types
python scripts/main.py --target ./my-project --include "*.py,*.js,*.yaml"

# Generate report
python scripts/main.py --target ./src --output secrets_report.json
```

### As Module

```python
from scripts.main import SecretsScanner

scanner = SecretsScanner()
results = scanner.scan_directory("./my-project")
scanner.generate_report(results, "report.json")
```

## Detected Secret Types

| Type | Pattern | Severity |
|------|---------|----------|
| AWS Access Key | AKIA... | CRITICAL |
| AWS Secret Key | Base64 40 chars | CRITICAL |
| GitHub Token | ghp_... | HIGH |
| Slack Token | xoxb-... | HIGH |
| Private Key | -----BEGIN... | CRITICAL |
| API Key | api[_-]?key... | HIGH |
| Password | password=... | MEDIUM |
| JWT Token | eyJ... | MEDIUM |

## Output Format

```json
{
  "scan_info": {
    "target": "./my-project",
    "timestamp": "2024-01-20T10:00:00Z",
    "files_scanned": 150,
    "git_history_scanned": true
  },
  "findings": [
    {
      "id": "SEC-001",
      "type": "aws_access_key",
      "severity": "CRITICAL",
      "file": "config.py",
      "line": 23,
      "match": "AKIAIOSFODNN7EXAMPLE",
      "entropy": 4.2,
      "verified": false
    }
  ],
  "summary": {
    "critical": 1,
    "high": 3,
    "medium": 5,
    "low": 2
  }
}
```

## Git History Scanning

Scan git commit history for secrets that may have been removed from current codebase:

```bash
python scripts/main.py --target ./my-project --scan-history --max-commits 100
```

## Skill Metadata

- **Name**: secrets-scanner-skill
- **Category**: security
- **Author**: Godlike Kimi Skills
- **Version**: 1.0.0
- **License**: MIT
