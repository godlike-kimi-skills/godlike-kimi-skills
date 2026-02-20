# Dependency Check Skill

Automated dependency vulnerability scanner for requirements.txt and package.json. Use when auditing code security, scanning for vulnerabilities, or when user mentions 'security', 'vulnerability', 'CVE'.

## Features

- **Multi-format support**: requirements.txt, package.json, Pipfile, go.mod
- **CVE database**: Check against National Vulnerability Database
- **License scanning**: Identify dependency licenses
- **Outdated detection**: Find outdated dependencies

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Command Line

```bash
# Scan requirements.txt
python scripts/main.py --file requirements.txt --format requirements

# Scan package.json
python scripts/main.py --file package.json --format npm

# Scan with custom output
python scripts/main.py --file requirements.txt --format requirements --output report.json

# Check for outdated packages
python scripts/main.py --file package.json --format npm --check-outdated
```

### As Module

```python
from scripts.main import DependencyChecker

checker = DependencyChecker()
results = checker.scan_file("requirements.txt", "requirements")
checker.generate_report(results, "report.json")
```

## Supported Formats

| Format | File Pattern | Description |
|--------|--------------|-------------|
| requirements | requirements*.txt | Python pip requirements |
| npm | package.json | Node.js/npm dependencies |
| pipfile | Pipfile.lock | Pipenv lock file |
| gomod | go.mod | Go modules |
| maven | pom.xml | Java Maven dependencies |

## Output Format

```json
{
  "scan_info": {
    "file": "requirements.txt",
    "format": "requirements",
    "timestamp": "2024-01-20T10:00:00Z",
    "total_dependencies": 25
  },
  "dependencies": [
    {
      "name": "requests",
      "version": "2.25.0",
      "latest_version": "2.31.0",
      "license": "Apache-2.0",
      "vulnerabilities": [
        {
          "cve_id": "CVE-2023-32681",
          "severity": "MEDIUM",
          "description": "Proxy-Authorization header leak",
          "fixed_in": "2.31.0"
        }
      ]
    }
  ],
  "summary": {
    "critical": 0,
    "high": 1,
    "medium": 3,
    "low": 2,
    "outdated": 8,
    "up_to_date": 17
  }
}
```

## CVE Severity Levels

- **CRITICAL**: Immediate action required, remote code execution possible
- **HIGH**: Significant security impact, should update soon
- **MEDIUM**: Moderate security concern, update recommended
- **LOW**: Minor security issue, update when convenient

## Skill Metadata

- **Name**: dependency-check-skill
- **Category**: security
- **Author**: Godlike Kimi Skills
- **Version**: 1.0.0
- **License**: MIT
