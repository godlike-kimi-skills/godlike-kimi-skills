---
name: code-metrics-skill
description: Code quality metrics analysis with cyclomatic complexity, line counts, duplicate code detection, and maintainability scoring. Use when measuring code quality, identifying complex functions, finding duplicate code, or generating quality reports. Supports Python with extensible architecture for other languages.
---

# Code Quality Metrics Skill

## Use When
- Measuring code complexity and maintainability
- Identifying high-complexity functions
- Detecting duplicate code blocks
- Generating code quality reports
- Tracking code metrics over time
- Enforcing code quality thresholds
- Analyzing code coverage of metrics

## Out of Scope
- Static security analysis (use security scanners)
- Performance profiling (use profilers)
- Dependency analysis
- Code style/linting (use linters)
- Test coverage analysis
- Architecture analysis
- Multi-language support (Python only currently)

## Quick Start

```python
from scripts.main import CodeMetricsAnalyzer, FileMetrics

# Initialize analyzer
analyzer = CodeMetricsAnalyzer("/path/to/project")

# Analyze single file
file_metrics = analyzer.analyze_file(Path("module.py"))
print(f"Complexity: {len(file_metrics.complexity)} functions")
print(f"Quality Score: {file_metrics.quality_score}/100")

# Analyze entire project
project = analyzer.analyze_project()
print(f"Total files: {project.total_files}")
print(f"Avg complexity: {project.avg_complexity:.2f}")
print(f"Quality Score: {project.quality_score:.1f}/100")

# Generate report
report = analyzer.generate_report(project, format="text")
print(report)
```

## Core Features

### Complexity Analysis
- Cyclomatic complexity per function
- Complexity classification (low/medium/high/very high)
- Aggregate complexity statistics
- Top complex functions identification

### Line Metrics
- Total, code, blank, and comment lines
- Comment ratio calculation
- Documentation coverage

### Duplicate Detection
- Code block similarity detection
- Configurable minimum block size
- Hash-based duplicate identification
- Cross-file duplicate detection

### Quality Scoring
- Maintainability index (0-100)
- Overall quality score
- File-by-file quality ratings
- Threshold-based alerts

## CLI Usage

```bash
# Analyze project
python scripts/main.py /path/to/project

# Exclude patterns
python scripts/main.py /path/to/project --exclude "*test*" --exclude "*venv*"

# JSON output
python scripts/main.py /path/to/project --format json --output report.json

# Analyze single file
python scripts/main.py analyze-file module.py

# Show complexity report
python scripts/main.py /path/to/project complexity

# Show duplicates
python scripts/main.py /path/to/project duplicates

# Filter by complexity
python scripts/main.py /path/to/project --min-complexity 10
```

## Complexity Classifications

| Level | Range | Action |
|-------|-------|--------|
| Low | 1-5 | Acceptable |
| Medium | 6-10 | Review recommended |
| High | 11-20 | Refactoring suggested |
| Very High | 21+ | Immediate attention |

## Quality Score Factors

### Positive Factors
- Good comment ratio (10-30%)
- Low complexity
- No duplicate code
- Reasonable file size

### Negative Factors
- High complexity functions
- Duplicate code blocks
- Large files (>1000 lines)
- Low comment ratio (<10%)

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| exclude_patterns | venv, test, etc. | Patterns to exclude |
| min_duplicate_lines | 5 | Minimum lines for duplicate detection |

## Report Output

### Text Format
```
============================================================
CODE QUALITY METRICS REPORT
============================================================

SUMMARY
----------------------------------------
Total Files: 42
Total Lines: 15,234
Code Lines: 12,100
Average Complexity: 4.52
Max Complexity: 25
High Complexity Functions: 8
Duplicate Blocks: 3
Overall Quality Score: 78.5/100

TOP 10 MOST COMPLEX FILES
----------------------------------------
  module.py: max complexity = 25
  utils.py: max complexity = 18
  ...
```

### JSON Format
```json
{
  "summary": {
    "total_files": 42,
    "total_lines": 15234,
    "avg_complexity": 4.52,
    "quality_score": 78.5
  },
  "files": [...]
}
```
