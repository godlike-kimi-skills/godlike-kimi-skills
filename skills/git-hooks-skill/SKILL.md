---
name: git-hooks-skill
description: Git hooks management for pre-commit, pre-push, Husky configuration, and custom hooks. Use when enforcing code quality, running tests before commits, validating commit messages, or automating development workflows. Supports shell and Python hooks, commit message validation, and Husky integration.
---

# Git Hooks Management Skill

## Use When
- Setting up pre-commit hooks for code quality
- Configuring pre-push hooks for test execution
- Validating commit message formats
- Creating custom Git hooks
- Setting up Husky for JavaScript projects
- Managing hook enable/disable states
- Testing hooks manually

## Out of Scope
- Git server-side hooks (update, post-receive)
- Complex CI/CD pipeline integration
- Webhook management
- GitHub/GitLab Actions configuration
- Advanced Git LFS hooks
- Complex multi-repo hook management

## Quick Start

```python
from scripts.main import GitHooksManager, HookType, CommitMessageConfig

# Initialize in git repository
hooks = GitHooksManager("/path/to/repo")

# Create pre-commit hook with linting
hooks.create_pre_commit_hook(
    lint_cmd="flake8 .",
    test_cmd="pytest tests/"
)

# Create commit message validator
config = CommitMessageConfig(
    allowed_types=["feat", "fix", "docs"],
    require_scope=True
)
hooks.create_commit_msg_hook(config)

# Enable hooks
hooks.enable_hook(HookType.PRE_COMMIT)
```

## Core Features

### Hook Types Supported
- **pre-commit**: Run before each commit
- **pre-push**: Run before each push
- **commit-msg**: Validate commit messages
- **prepare-commit-msg**: Modify commit messages
- **post-checkout**: After checkout
- **post-merge**: After merge
- **pre-rebase**: Before rebase

### Commit Message Validation
- Conventional Commits format support
- Custom type prefixes
- Scope requirements
- Message length limits
- Custom regex patterns

### Husky Integration
- Husky v4+ configuration
- Modern Husky (v7+) setup
- npm script integration
- Package.json hooks

## CLI Usage

```bash
# List all hooks
python scripts/main.py --repo /path/to/repo list

# Create pre-commit hook
python scripts/main.py --repo . create-pre-commit --lint "flake8 ." --test "pytest"

# Create pre-push hook
python scripts/main.py --repo . create-pre-push --test "pytest --cov"

# Create commit message validator
python scripts/main.py --repo . create-commit-msg --types "feat,fix,docs" --max-len 72

# Manage hooks
python scripts/main.py --repo . enable pre-commit
python scripts/main.py --repo . disable pre-commit
python scripts/main.py --repo . delete pre-commit

# Test hooks manually
python scripts/main.py --repo . run pre-commit

# Test commit message
python scripts/main.py --repo . test-msg "feat(auth): add login functionality"

# Setup Husky
python scripts/main.py --repo . setup-husky
python scripts/main.py --repo . install-husky
```

## Commit Message Format

### Conventional Commits
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation
- **style**: Formatting
- **refactor**: Code restructuring
- **test**: Tests
- **chore**: Maintenance

### Example
```
feat(auth): implement OAuth2 login

Add Google and GitHub OAuth providers for user authentication.

Closes #123
```

## Hook Templates

### Python-based Hook
```python
#!/usr/bin/env python3
import sys
import subprocess

def main():
    # Run linting
    result = subprocess.run(["flake8", "."], capture_output=True)
    if result.returncode != 0:
        print("Linting failed!")
        print(result.stdout.decode())
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### Shell-based Hook
```bash
#!/bin/sh
echo "Running pre-commit checks..."

# Run tests
if ! pytest tests/; then
    echo "Tests failed!"
    exit 1
fi

exit 0
```
