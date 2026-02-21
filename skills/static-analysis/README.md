# Static Analysis

<p align="center">
  <strong>Professional Python Code Static Analysis Tool</strong><br>
  Code quality, complexity analysis, security scanning, and style checking
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#documentation">Documentation</a> •
  <a href="#license">License</a>
</p>

---

## Features

- ✅ **Complexity Analysis** - Cyclomatic and cognitive complexity metrics
- ✅ **Security Scanning** - Detect dangerous functions, hardcoded secrets, SQL injection
- ✅ **Style Checking** - PEP8 compliance, line length, indentation
- ✅ **Code Metrics** - LOC, functions, classes, maintainability index
- ✅ **Multi-format Reports** - HTML, JSON, and Markdown
- ✅ **Baseline Comparison** - Track code quality improvements

## Installation

### Prerequisites

- Python 3.10+
- pip

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Analyze a Project

```bash
python main.py --action analyze --target ./src
```

### 2. Security Scan

```bash
python main.py --action security --target ./src
```

### 3. Check Complexity

```bash
python main.py --action complexity --target ./src --min-complexity 10
```

### 4. Generate Config Template

```bash
python main.py --action generate-config
```

## Documentation

### Actions

| Action | Description |
|--------|-------------|
| `analyze` | Full analysis (complexity + security + style) |
| `complexity` | Complexity analysis only |
| `security` | Security scanning only |
| `style` | Style checking only |
| `compare` | Compare with baseline report |
| `generate-config` | Generate configuration template |

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--action` | string | required | Action to perform |
| `--target` | string | required | Target file or directory |
| `--output-dir` | string | ./analysis-results | Output directory |
| `--exclude-patterns` | string | built-in | Comma-separated exclude patterns |
| `--min-complexity` | integer | 10 | Minimum complexity threshold |
| `--max-line-length` | integer | 100 | Maximum line length |
| `--strict-mode` | boolean | false | Enable strict checking |
| `--baseline-path` | string | - | Baseline report for comparison |
| `--format` | string | html | Report format (html/json/markdown) |

### Examples

#### Full Project Analysis

```bash
python main.py --action analyze \
  --target ./my-project \
  --output-dir ./reports \
  --exclude-patterns tests,examples,__pycache__
```

#### Strict Security Scan

```bash
python main.py --action security \
  --target ./src \
  --strict-mode
```

#### Complexity with Custom Threshold

```bash
python main.py --action complexity \
  --target ./src \
  --min-complexity 5 \
  --format json
```

#### Compare with Baseline

```bash
# Generate baseline
python main.py --action analyze \
  --target ./src \
  --format json \
  --output-dir ./baseline

# Compare later
python main.py --action compare \
  --target ./src \
  --baseline-path ./baseline/report_20240101_120000.json
```

## Reports

### HTML Report

Rich visual report with:
- Summary cards
- Complexity issues table
- Security issues by severity
- Style violations
- File metrics

### JSON Report

Structured data for CI/CD integration:
```json
{
  "timestamp": "2026-02-21T10:30:00",
  "target": "./src",
  "total_files": 25,
  "total_lines": 5000,
  "complexity_issues": [...],
  "security_issues": [...],
  "style_issues": [...]
}
```

### Markdown Report

GitHub-friendly format for PR comments and documentation.

## CI/CD Integration

### GitHub Actions

```yaml
name: Code Quality
on: [push, pull_request]

jobs:
  static-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      
      - name: Install Dependencies
        run: pip install -r requirements.txt
      
      - name: Run Analysis
        run: |
          python main.py --action analyze \
            --target ./src \
            --format json
      
      - name: Check Security
        run: |
          if grep -q '"severity": "critical"' ./analysis-results/*.json; then
            echo "Critical security issues found!"
            exit 1
          fi
      
      - name: Upload Report
        uses: actions/upload-artifact@v4
        with:
          name: analysis-report
          path: ./analysis-results/
```

## Complexity Guidelines

| Complexity | Rating | Action |
|------------|--------|--------|
| 1-10 | Good | No action needed |
| 11-20 | Moderate | Consider refactoring |
| 21-50 | High | Refactor recommended |
| 50+ | Very High | Refactor required |

## Security Rules

| Rule | Severity | Description |
|------|----------|-------------|
| dangerous_function_eval | Critical | Use of eval() is dangerous |
| dangerous_function_exec | Critical | Use of exec() is dangerous |
| hardcoded_secret | High | Possible hardcoded credentials |
| potential_sql_injection | High | SQL injection vulnerability |
| unsafe_yaml_load | High | Use yaml.safe_load() instead |
| unsafe_pickle | High | Deserializing untrusted data |

## Maintainability Index

| Range | Rating | Description |
|-------|--------|-------------|
| 85-100 | Excellent | Easy to maintain |
| 65-84 | Good | Acceptable range |
| 0-64 | Poor | Needs refactoring |

## Architecture

```
static-analysis/
├── main.py              # Main entry point
├── skill.json           # Skill manifest
├── SKILL.md             # Chinese documentation
├── README.md            # English documentation
├── LICENSE              # MIT License
├── requirements.txt     # Dependencies
└── tests/               # Test suite
    ├── __init__.py
    └── test_static_analysis.py
```

### Core Components

- **StaticAnalyzer** - Main analysis orchestrator
- **ComplexityAnalyzer** - Cyclomatic complexity calculation
- **SecurityScanner** - Security vulnerability detection
- **StyleChecker** - PEP8 style checking
- **MetricsCollector** - Code metrics collection
- **ReportGenerator** - Multi-format report generation

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Part of [Godlike Kimi Skills](https://github.com/godlike-kimi-skills)
- Built with Python AST module

---

<p align="center">
  Made with ❤️ by Godlike Kimi Skills
</p>
