---
name: git-assistant
description: Git operations and workflow assistance. Use when working with Git repositories, creating commits, managing branches, handling merges, or following Git workflows for software development.
---

# Git Assistant

Git operations and workflow assistance for software development.

## Features

- Smart commit message generation
- Branch management
- Workflow guidance
- Repository status overview

## Usage

### Smart Commit

```bash
python D:/kimi/skills/git-assistant/scripts/git_helper.py commit
```

Analyzes staged changes and suggests commit message.

### Branch Operations

```bash
# Create feature branch
python D:/kimi/skills/git-assistant/scripts/git_helper.py branch feature login-page

# List branches with status
python D:/kimi/skills/git-assistant/scripts/git_helper.py branches

# Switch branch
python D:/kimi/skills/git-assistant/scripts/git_helper.py switch main
```

### Workflow

```bash
# Start new feature
python D:/kimi/skills/git-assistant/scripts/git_helper.py start-feature auth-system

# Finish feature (merge to main)
python D:/kimi/skills/git-assistant/scripts/git_helper.py finish-feature
```

### Repository Status

```bash
python D:/kimi/skills/git-assistant/scripts/git_helper.py status
```

## Supported Workflows

- **GitHub Flow** - Feature branch workflow
- **Git Flow** - Release-based workflow
- **Trunk-based** - Continuous integration
