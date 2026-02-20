---
name: git-analyzer-skill
description: Git repository analysis and visualization tool. Use when analyzing Git repositories, checking commit history, counting code statistics, visualizing branches, or when user mentions 'git', 'repository', 'commit history', 'code stats', 'lines of code', 'contributors', 'branch visualization', 'git log', 'git diff', 'blame'. Supports commit analysis, code metrics, contributor statistics, branch visualization, and repository health checks.
---

# Git Analyzer Skill

Git repository analysis tool for understanding code history, contributor activity, and repository metrics.

## Capabilities

- **Commit History Analysis**: Log viewing, author statistics, time range filtering
- **Code Statistics**: Lines of code, file counts, language distribution
- **Contributor Analysis**: Top contributors, commit frequency, activity patterns
- **Branch Visualization**: Branch tree, merge history, divergence tracking
- **Repository Health**: File size check, large files detection, commit message quality

## Use When

- Analyzing Git repository history
- Finding top contributors to a project
- Visualizing branch structure and merges
- Counting lines of code by language
- Detecting large files in repository
- Checking commit patterns and frequency
- Generating repository statistics reports

## Out of Scope

- Git repository hosting setup
- CI/CD pipeline configuration
- Git hooks management
- Submodule operations
- Patch creation and application
- Repository mirroring

## Quick Start

### Analyze Repository

```python
from scripts.main import GitAnalyzer

analyzer = GitAnalyzer("/path/to/repo")

# Get commit history
commits = analyzer.get_commit_history(limit=10)

# Get contributor stats
contributors = analyzer.get_contributor_stats()

# Count lines of code
stats = analyzer.get_code_stats()
```

### Branch Visualization

```python
# Get branch tree
branches = analyzer.get_branch_tree()

# Find branch divergence
merge_bases = analyzer.find_merge_bases("main", "feature-branch")
```

### CLI Usage

```bash
# Repository overview
python scripts/main.py /path/to/repo

# Commit history
python scripts/main.py /path/to/repo --commits --limit 20

# Contributor stats
python scripts/main.py /path/to/repo --contributors

# Code statistics
python scripts/main.py /path/to/repo --stats

# Branch visualization
python scripts/main.py /path/to/repo --branches
```

## Reference

See [references/git_commands.md](references/git_commands.md) for Git command reference.
