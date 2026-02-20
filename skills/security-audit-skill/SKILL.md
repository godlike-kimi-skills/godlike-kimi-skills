# Security Audit Skill

Automated code security auditing tool for Python, JavaScript, and Java. Use when auditing code security, scanning for vulnerabilities, or when user mentions 'security', 'vulnerability', 'CVE'.

## Features

- **Multi-language support**: Python, JavaScript, Java
- **Vulnerability scanning**: Detect common security issues
- **Security report**: Generate detailed audit reports
- **Compliance checking**: OWASP Top 10, CWE detection

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Command Line

```bash
python scripts/main.py --target /path/to/code --language python
python scripts/main.py --target /path/to/code --language javascript
python scripts/main.py --target /path/to/code --language java --output report.json
```

### As Module

```python
from scripts.main import SecurityAuditor

auditor = SecurityAuditor(language="python")
results = auditor.audit("/path/to/code")
auditor.generate_report(results, "report.json")
```

## Supported Vulnerabilities

### Python
- SQL Injection
- Command Injection
- Path Traversal
- Hardcoded Secrets
- Unsafe Deserialization

### JavaScript
- XSS vulnerabilities
- Prototype Pollution
- Insecure Dependencies
- eval() usage
- InnerHTML assignments

### Java
- SQL Injection
- XXE vulnerabilities
- Insecure Randomness
- Weak Cryptography
- Unsafe Reflection

## Output Format

```json
{
  "scan_info": {
    "target": "/path/to/code",
    "language": "python",
    "timestamp": "2024-01-20T10:00:00Z",
    "total_files": 42
  },
  "vulnerabilities": [
    {
      "id": "PY-001",
      "severity": "HIGH",
      "type": "sql_injection",
      "file": "app.py",
      "line": 23,
      "description": "Potential SQL injection vulnerability",
      "recommendation": "Use parameterized queries"
    }
  ],
  "summary": {
    "critical": 0,
    "high": 2,
    "medium": 5,
    "low": 8,
    "info": 3
  }
}
```

## Skill Metadata

- **Name**: security-audit-skill
- **Category**: security
- **Author**: Godlike Kimi Skills
- **Version**: 1.0.0
- **License**: MIT
